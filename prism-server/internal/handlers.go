package internal

import (
	"encoding/json"
	"maps"
	"math"
	"math/rand/v2"
	"net/http"
	"time"
)

type Response struct {
	Message string `json:"message"`
}

type WeightedStock struct {
	Ticker   string `json:"ticker"`
	Quantity uint   `json:"quantity"`
}

type Handlers struct {
	db          *Database
	userContext map[string]*RequestContext // XXX: Using large string as hash might be bad
	timeToLive  time.Duration
}

func NewHandlers(db *Database, uc map[string]*RequestContext, timeToLive time.Duration) Handlers {
	return Handlers{db, uc, timeToLive}
}

// Note, that hitting this endpoint over-writes previous RequestContext.
// This means that a user should keep track of whether they are responding
// to the right piece of context.
// TODO: Think about whether we need to force users to only compete from one device, to avoid race conditions.
// TODO: Handle context management
func (h *Handlers) GetHandler(w http.ResponseWriter, r *http.Request) {
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
		StartDate:        startDate.Local().Local().String(),
		EndDate:          endDate.Local().String(),
		Age:              rand.IntN(MAX_AGE-MIN_AGE) + MIN_AGE,
		EmploymentStatus: employed,
		Salary:           salary,
		Budget:           budget,
		Dislikes:         dislikes,
	}

	// Map context to the individual user, identified by their API token.
	h.userContext[apiKey] = &randomContext

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

// @cyrus wym by this?
// TODO: Handle context management
func (h *Handlers) PostHandler(w http.ResponseWriter, r *http.Request) {
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

	userContext, ok := h.userContext[apiKey]
	// Remove key from map, as it has been consumed now. On error, ignores.
	delete(h.userContext, apiKey)

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
[{"ticker": "AAPL", "quantity": 1}, {"ticker": "MSFT", quantity: 10}]`, http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	// For now, just respond with the same values.
	// TODO: This should go away.
	stocksStr, err := json.Marshal(stocks)
	if err != nil {
		http.Error(w, "Unable to marshal weighted stock list. If you see this error, please contact an event administrator.", http.StatusInternalServerError)
		return
	}

	// FIXME: Evaluation left.

	// resp := Response{
	// 	Message: "Request accepted, payload: " + string(stocksStr)
	// }

	// Respond with JSON.
	w.Header().Set("Content-Type", "application/json")
	w.Write(stocksStr)
	// json.NewEncoder(w).Encode(resp)
}
