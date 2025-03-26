package internal

import (
	"encoding/json"
	"io"
	"net/http"
)

type Response struct {
	Message string `json:"message"`
}

func GetHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed, GET only", http.StatusMethodNotAllowed)
		return
	}

	apiKey := r.Header.Get("X-API-Code")
	// FIXME: check this with many apis else error
	if apiKey != "test" {
		http.Error(w, "Unauthorized - invalid API key", http.StatusUnauthorized)
		return
	}

}

// postHandler handles POST requests to the /postpath endpoint.
func PostHandler(w http.ResponseWriter, r *http.Request) {
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
