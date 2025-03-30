package internal

import (
	"encoding/json"
	"io"
	"net/http"
	"time"
)

type Response struct {
	Message string `json:"message"`
}

type Handlers struct {
	db          *Database
	userContext map[string]*RequestContext // XXX: Using large string as hash might be bad
}

func NewHandlers(db *Database, uc map[string]*RequestContext) Handlers {
	return Handlers{db, uc}
}

// TODO: Handle context management
func (h *Handlers) GetHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed, GET only", http.StatusMethodNotAllowed)
		return
	}

	apiKey := r.Header.Get("X-API-Code")
	validKey, err := ValidateApiKey(apiKey, h.db)
	if err != nil {
		http.Error(w, "Database error - could not query DB: "+err.Error(), http.StatusInternalServerError)
		return
	}

	if !validKey {
		http.Error(w, "Unauthorized - invalid API key", http.StatusUnauthorized)
	}
	// FIXME: Generate and return response
	// generate random context
	randomContext := RequestContext{
		timestamp:        time.Now(),
		startDate:        "01-01-01",
		endDate:          "02-01-01",
		age:              30,
		employmentStatus: false,
		salary:           30000.00,
		budget:           30000.00,
		dislikes:         []string{"gala", "leather jackets"},
	}

	// map it to user
	h.userContext[apiKey] = &randomContext

	// generate text based on context
	content := "Julie, 23, loves Nvidia"
	resp := Response{
		Message: "Request accepted, payload: " + string(content),
	}
	// Write JSON response to response writer
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

// postHandler handles POST requests to the /postpath endpoint.?
// TODO: Handle context management
func (h *Handlers) PostHandler(w http.ResponseWriter, r *http.Request) {
	// Only allow POST requests.
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Check for the API code in the header "X-API-Code".
	apiKey := r.Header.Get("X-API-Code")
	validKey, err := ValidateApiKey(apiKey, h.db)
	if err != nil {
		http.Error(w, "Database error - could not query DB: "+err.Error(), http.StatusInternalServerError)
		return
	}

	if !validKey {
		http.Error(w, "Unauthorized - invalid API key", http.StatusUnauthorized)
	}

	thisUserContext := h.userContext[apiKey]

	// Read the request body.
	// FIXME: Handle request body
	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Bad request", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	// Prepare a response.
	// FIXME: Calculate response
	resp := Response{
		Message: "Request accepted, payload: " + string(body),
	}

	// Respond with JSON.
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}
