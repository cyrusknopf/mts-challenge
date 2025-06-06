package internal

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os/exec"
	"strings"
	"sync"
	"time"
)

var port int = 1

type Response struct {
	Message string `json:"message"`
}

type LLMResponse struct {
	Status int    `json:"status"`
	Body   string `json:"body"`
}

type WeightedStock struct {
	Ticker   string `json:"ticker"`
	Quantity uint   `json:"quantity"`
}

type HandlersConfig struct {
	db               *Database
	userContext      map[string]*RequestContext
	lastRequestTime  map[string]time.Time
	maxDeltaSpamTime time.Duration // Number of seconds
	userContextMutex sync.RWMutex
	pyServerMutex    sync.RWMutex
	timeToLive       time.Duration
	evalDir          string
	apiKey           string
	numLLMServers    int
}

func NewHandlers(db *Database, uc map[string]*RequestContext, maxDeltaSpamTime time.Duration, timeToLive time.Duration, evalDir string, apiKey string, numLLMServers int) HandlersConfig {
	return HandlersConfig{db, uc, make(map[string]time.Time, 0), maxDeltaSpamTime, sync.RWMutex{}, sync.RWMutex{}, timeToLive, evalDir, apiKey, numLLMServers}
}

type User struct {
	ID                 int       `json:"-"`
	APIKey             string    `json:"-"`
	TeamName           string    `json:"teamname"`
	Points             float64   `json:"points"`
	Profit             float64   `json:"profit"`
	LastSubmissionTime time.Time `json:"last_submission_time"`
}

func (h *HandlersConfig) InfoHandler(w http.ResponseWriter, r *http.Request) {
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
		fmt.Printf("Error: %v\n", err)
		http.Error(w, "Unauthorized - invalid or missing X-API-Code header. You should have received on X-API-Code per team.", http.StatusUnauthorized)
		return
	}

	row, err := h.db.QueryRow("select * from teams where api_key = $1", apiKey)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		http.Error(w, "Database error - could not query DB: "+err.Error()+"\n\nIf you see this error, please contact an event administrator.", http.StatusInternalServerError)
		return
	}

	var user User
	err = row.Scan(&user.ID, &user.APIKey, &user.TeamName, &user.Points, &user.Profit, &user.LastSubmissionTime)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		http.Error(w, "Unable to parse user information, contact administrator if this issue persists", http.StatusInternalServerError)
		return
	}

	out, err := json.Marshal(user)
	if err != nil {
		http.Error(w, "Unable to marshal user information, contact administrator if this issue persists.", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.Write(out)
}

// Note, that hitting this endpoint over-writes previous RequestContext.
// This means that a user should keep track of whether they are responding
// to the right piece of context.
// TODO: Think about whether we need to force users to only compete from one device, to avoid race conditions.
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

	// h.userContextMutex.Lock()
	// userkastTime, found := h.lastRequestTime[apiKey]
	// h.userContextMutex.Unlock()
	// if !found {
	// 	h.userContextMutex.Lock()
	// 	h.lastRequestTime[apiKey] = time.Now()
	// 	h.userContextMutex.Unlock()
	// } else {
	// 	if userLastTime.Add(h.maxDeltaSpamTime).After(time.Now()) {
	// 		// Spam detected
	// 		// Penalise
	// 		_, err = h.db.Exec("UPDATE teams SET profit = profit * 0.75, points = points * 0.75, last_submission_time = NOW() WHERE api_key = $1", apiKey)
	// 		if err != nil {
	// 			fmt.Printf("%v\n", err)
	// 			http.Error(w, "An error was encountered updating the database, please reach out to the administrator if this keeps happening.", http.StatusInternalServerError)
	// 			return
	// 		}
	// 		// Return, do not service.
	// 		http.Error(w, fmt.Sprintf("You have re-requested within %v duration, please reduce your spam. You have been penalised a little bit.", h.maxDeltaSpamTime), http.StatusInternalServerError)
	// 		return
	// 	} else {
	// 		h.userContextMutex.Lock()
	// 		h.lastRequestTime[apiKey] = time.Now()
	// 		h.userContextMutex.Unlock()
	// 	}
	// }

	randomContext := GenerateRandomContext()

	// Generate LLM based text. For now, it JSONs the values.
	content, err := json.Marshal(randomContext)
	if err != nil {
		http.Error(w, "Error while marshalling json. If you see this, please contact an event administrator.", http.StatusInternalServerError)
		return
	}

	/*
	   Implements a round robin scheduler for requesting from the four Python LLM servers.
	   Requests from the following ports, in order:
	       - 8001
	       - 8002
	       - 8003
	       - 8004
	    Locks around the port update since it is shared amongst goroutines that all serve the go HTTP server (i think)
	*/
	// h.pyServerMutex.Lock()
	// // Base URL
	// base_url := "http://prism-llm:800%d/generate"
	// // Format with the port final number
	// url := fmt.Sprintf(base_url, port)
	// // Print serverside for debug
	// fmt.Printf("Requesting from %s\n", url)
	// // Cycle through values 1,2,3,4
	// port = port%h.numLLMServers + 1
	// // Unlock
	// h.pyServerMutex.Unlock()
	// Make the request
	// resp, err := http.Post(url, "application/json", bytes.NewBuffer(content))
	// if err != nil {
	// 	http.Error(w, "Failed to POST to PyServer"+err.Error()+"\n\nIf you see this please contact Cyrus or Sai", http.StatusInternalServerError)
	// 	return
	// }
	// defer resp.Body.Close()

	// Read the response body
	// llm_resp, err := io.ReadAll(resp.Body)
	// if err != nil {
	// 	fmt.Println("Error reading LLM response body:", err)
	// 	return
	// }

	// Unmarshal the response into the LLMResponse struct
	// var llmResp LLMResponse
	// err = json.Unmarshal(llm_resp, &llmResp)
	// if err != nil {
	// 	fmt.Println("Error unmarshalling LLM response:", err)
	// 	return
	// }

	// Set the message to be just the "body" of the response
	// resp_to_user := Response{
	// 	Message: llmResp.Body,
	// }
	resp_to_user := Response{
		Message: string(content),
	}

	// Map context to the individual user, identified by their API token.
	h.userContextMutex.Lock()
	// Set the time to now instead of pre-generation
	randomContext.Timestamp = time.Now()
	h.userContext[apiKey] = &randomContext
	h.userContextMutex.Unlock()

	// Write JSON response to response writer
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp_to_user)
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
	delete(h.lastRequestTime, apiKey)
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
		fmt.Printf("error: %v | %s\n", err, out.String())
		http.Error(w, "Error during unmarshalling.", http.StatusInternalServerError)
		return
	}

	if !response.Passed {
		if len(response.Error) > 0 {
			if response.Points == -1.0 {
				// Penalise profit and points to 0.95%.
				_, err = h.db.Exec("UPDATE teams SET profit = profit * 0.75, points = points * 0.75, last_submission_time = NOW() WHERE api_key = $1", apiKey)
				if err != nil {
					fmt.Printf("%v\n", err)
					http.Error(w, "An error was encountered updating the database, please reach out to the administrator if this keeps happening.", http.StatusInternalServerError)
					return
				}
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
