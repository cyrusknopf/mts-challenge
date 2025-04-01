package internal

import (
	"encoding/json"
	"fmt"
	"maps"
	"math"
	"math/rand/v2"
	"net/http"
	"os/exec"
	"strings"
	"sync"
	"time"
)

type Response struct {
	Message string `json:"message"`
}

type WeightedStock struct {
	Ticker   string `json:"ticker"`
	Quantity uint   `json:"quantity"`
}

type HandlersConfig struct {
	db               *Database
	userContext      map[string]*RequestContext // XXX: Using large string as hash might be bad
	userContextMutex sync.RWMutex
	timeToLive       time.Duration
	evalDir          string
	apiKey           string
}

func NewHandlers(db *Database, uc map[string]*RequestContext, timeToLive time.Duration, evalDir string, apiKey string) HandlersConfig {
	return HandlersConfig{db, uc, sync.RWMutex{}, timeToLive, evalDir, apiKey}
}

// Note, that hitting this endpoint over-writes previous RequestContext.
// This means that a user should keep track of whether they are responding
// to the right piece of context.
// TODO: Think about whether we need to force users to only compete from one device, to avoid race conditions.
// TODO: Handle context management
func (h *HandlersConfig) GetHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed, only GET allowed", http.StatusMethodNotAllowed)
		return
	}

	apiKey := r.Header.Get("X-API-Code")
	validKey, err := ValidateAPIKey(apiKey, h.db)
	if err != nil {
		http.Error(w, "Database error - could not query DB: "+err.Error()+"\n\nIf you see this error, please contact an event administrator.", http.StatusInternalServerError)
		return
	}

	if !validKey {
		http.Error(w, "Unauthorized - invalid or missing X-API-Code header. You should have received on X-API-Code per team.", http.StatusUnauthorized)
		return
	}

	dislikesSet := make(map[string]struct{})
	n := rand.IntN(len(UNIQUE_INDUSTRIES) - 6)
	// We leave at least 6 industries free to invest.
	//
	// Also, this will not guarantee that you have n disliked sectors,
	// just that at most it is n. This is because, on duplicate hit, we
	// do not redo the iteration.
	for range n {
		s := UNIQUE_INDUSTRIES[rand.IntN(len(UNIQUE_INDUSTRIES))]
		if _, ok := dislikesSet[s]; !ok {
			// This is a new industry, we add it in.
			dislikesSet[s] = struct{}{}
		}
	}
	dislikes := make([]string, 0)
	for k := range maps.Keys(dislikesSet) {
		if len(k) > 0 {
			dislikes = append(dislikes, k)
		}
	}

	startDate, endDate := randomDateRange()

	// More likely to be employed than unemployed.
	employed := rand.IntN(4) != 0

	salary := math.Round(math.Abs(rand.NormFloat64()*SALARY_STD + SALARY_MEAN))
	budget := math.Round(math.Abs(rand.NormFloat64()*BUDGET_STD+BUDGET_MEAN) * salary)

	if !employed {
		// Force salary to 0, if unemployed. Still gives budget to invest.
		salary = 0.0
	}

	randomContext := RequestContext{
		Timestamp:        time.Now(),
		StartDate:        startDate.Local().Format(time.RFC3339),
		EndDate:          endDate.Local().Format(time.RFC3339),
		Age:              rand.IntN(MAX_AGE-MIN_AGE) + MIN_AGE,
		EmploymentStatus: employed,
		Salary:           salary,
		Budget:           budget,
		Dislikes:         dislikes,
	}

	// Map context to the individual user, identified by their API token.
	h.userContextMutex.Lock()
	h.userContext[apiKey] = &randomContext
	h.userContextMutex.Unlock()

	// Generate LLM based text. For now, it JSONs the values.
	content, err := json.Marshal(randomContext)
	if err != nil {
		http.Error(w, "Error while marshalling json. If you see this, please contact an event administrator.", http.StatusInternalServerError)
		return
	}

	// FIXME: the response needs changing, after been put through LLM

	// resp := Response{
	// 	Message: "Request accepted, payload: " + string(content),
	// }
	// Write JSON response to response writer
	w.Header().Set("Content-Type", "application/json")
	// json.NewEncoder(w).Encode(resp)
	w.Write(content)
}

type EvaluationData struct {
	Context *RequestContext `json:"context"`
	Stocks  []WeightedStock `json:"stocks"`
}

type EvaluationResponse struct {
	Passed bool    `json:"passed"`
	Profit float64 `json:"profit"`
	Points float64 `json:"points"`
	Error  string  `json:"error"`
}

// @cyrus wym by this?
// TODO: Handle context management
func (h *HandlersConfig) PostHandler(w http.ResponseWriter, r *http.Request) {
	// Only allow POST requests.
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// TODO: This code is duplicated, we should move this into its own function.
	// Check for the API code in the header "X-API-Code".
	apiKey := r.Header.Get("X-API-Code")
	validKey, err := ValidateAPIKey(apiKey, h.db)
	if err != nil {
		http.Error(w, "Database error - could not query DB: "+err.Error(), http.StatusInternalServerError)
		return
	}

	if !validKey {
		http.Error(w, "Unauthorized - invalid or missing X-API-Code header. You should have received on X-API-Code per team.", http.StatusUnauthorized)
		return
	}

	h.userContextMutex.Lock()
	userContext, ok := h.userContext[apiKey]
	// Remove key from map, as it has been consumed now. On error, ignores.
	delete(h.userContext, apiKey)
	h.userContextMutex.Unlock()

	// Check whether they have requested the context before.
	if !ok {
		http.Error(w, "You have not requested before or have answered the request, please try a GET request to the /request endpoint.\nIf you are trying to answer requests from multiple machines, you will get a race condition so please only work from one computer at a time.", http.StatusForbidden)
		return
	}

	// Check whether the context is fresh, i.e. the timestamp and TTL is after now.
	if !userContext.Timestamp.Add(h.timeToLive).After(time.Now()) {
		http.Error(w, "Context expired, you responded too slowly boohoo :(... Try again with a faster computer :P.", http.StatusTeapot)
		return
	}

	// Read the request body.
	var stocks []WeightedStock
	jsonReader := json.NewDecoder(r.Body)
	err = jsonReader.Decode(&stocks)
	if err != nil {
		http.Error(w, `Poorly formatted input.

Example expected format:
[{"ticker": "AAPL", "quantity": 1}, {"ticker": "MSFT", "quantity": 10}]`, http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	// For now, just respond with the same values.
	evalData := EvaluationData{Stocks: stocks, Context: userContext}
	evalDataStr, err := json.Marshal(evalData)
	if err != nil {
		http.Error(w, "Unable to marshal weighted stock list. If you see this error, please contact an event administrator.", http.StatusInternalServerError)
		return
	}

	// FIXME: Evaluation left.
	var out strings.Builder
	subproc := exec.Command("/usr/bin/python",
		fmt.Sprintf("%s/main.py", h.evalDir),
		"--apikey", h.apiKey,
		"--basedir", h.evalDir,
	)
	subproc.Stdin = strings.NewReader(string(evalDataStr))
	subproc.Stdout = &out
	subproc.Stderr = &out
	if err = subproc.Run(); err != nil {
		fmt.Printf("error: %v\n", err)
		http.Error(w, "Error during evaluation.", http.StatusInternalServerError)
		return
	}

	var response EvaluationResponse
	err = json.Unmarshal([]byte(out.String()), &response)
	if err != nil {
		fmt.Printf("error: %v\n", err)
		http.Error(w, "Error during unmarshalling.", http.StatusInternalServerError)
		return
	}

	if !response.Passed {
		if len(response.Error) > 0 {
			// Penalise profit and points to 0.95%.
			_, err = h.db.Exec("UPDATE teams SET profit = profit * 0.95, points = points * 0.95, last_submission_time = NOW() WHERE api_key = $1", apiKey)
			if err != nil {
				fmt.Printf("%v\n", err)
				http.Error(w, "An error was encountered updating the database, please reach out to the administrator if this keeps happening.", http.StatusInternalServerError)
				return
			}
			// Respond accordingly to tell them they fucked up.
			http.Error(w, fmt.Sprintf("Error encountered while evaluation of input: [%s]. This is most likely a you problem. ", response.Error), http.StatusTeapot)
			return
		} else {
			http.Error(w, "Error encountered while evaluation of input, but no information was provided about the error. Please reach out to the administrator if this persists.\n", http.StatusTeapot)
			return
		}
	}

	_, err = h.db.Exec("UPDATE teams SET profit = profit + $1, points = points + $2, last_submission_time = NOW() WHERE api_key = $3", response.Profit, response.Points, apiKey)
	if err != nil {
		fmt.Printf("%v\n", err)
		http.Error(w, "An error was encountered updating the database, please reach out to the administrator if this keeps happening.", http.StatusInternalServerError)
		return
	}

	// Respond with JSON.
	w.Header().Set("Content-Type", "application/json")
	w.Write([]byte(out.String()))
}
