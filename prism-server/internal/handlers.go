package internal

import (
	"encoding/json"
	"io"
	"net/http"
)

type Response struct {
	Message string `json:"message"`
}

type Handlers struct {
	db *Database
}

func NewHandlers(db *Database) Handlers {
	return Handlers{db}
}

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

	content := "Julie, 23, loves Nvidia"

	if validKey {
		resp := Response{
			Message: "Request accepted, payload: " + string(content),
		}
		// Write JSON response to response writer
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(resp)
	} else {
		http.Error(w, "Unauthorized - invalid API key", http.StatusUnauthorized)
	}
}

// postHandler handles POST requests to the /postpath endpoint.
func (_ *Handlers) PostHandler(w http.ResponseWriter, r *http.Request) {
	// Only allow POST requests.
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Check for the API code in the header "X-API-Code".
	// FIXME: check this with many apis else error
	apiKey := r.Header.Get("X-API-Code")
	if apiKey != "test" {
		http.Error(w, "Unauthorized - invalid API key", http.StatusUnauthorized)
		return
	}

	// Read the request body.
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
