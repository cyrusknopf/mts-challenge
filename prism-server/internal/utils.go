package internal

import (
	"fmt"
	"time"
)

type RequestContext struct {
	timestamp        time.Time
	startDate        string
	endDate          string
	age              int
	employmentStatus bool
	salary           float32
	budget           float32
	dislikes         []string
}

func ValidateApiKey(api_key string, db *Database) (bool, error) {
	var exists bool
	query := `SELECT EXISTS(SELECT 1 FROM teams WHERE api_key = $1);`

	// Pass api_key as a parameter to query
	row, err := db.QueryRow(query, api_key)
	if err != nil {
		return false, fmt.Errorf("Failed to query database: %w", err)
	}

	// Now scan the row result to see if exists, storing the result in `exists`
	err = row.Scan(&exists)
	if err != nil {
		return false, fmt.Errorf("Failed to scan result: %w", err)
	}

	return exists, nil
}
