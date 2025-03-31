package internal

import (
	"fmt"
	"math/rand/v2"
	"time"
)

type RequestContext struct {
	Timestamp        time.Time `json:"timestamp"`
	StartDate        string    `json:"start"`
	EndDate          string    `json:"end"`
	Age              int       `json:"age"`
	EmploymentStatus bool      `json:"employed"`
	Salary           float64   `json:"salary"`
	Budget           float64   `json:"budget"`
	Dislikes         []string  `json:"dislikes"`
}

func ValidateAPIKey(apiKey string, db *Database) (bool, error) {
	var exists bool
	query := `SELECT EXISTS(SELECT 1 FROM teams WHERE api_key = $1);`

	// Pass api_key as a parameter to query
	row, err := db.QueryRow(query, apiKey)
	if err != nil {
		return false, fmt.Errorf("failed to query database: %w", err)
	}

	// Now scan the row result to see if exists, storing the result in `exists`
	err = row.Scan(&exists)
	if err != nil {
		return false, fmt.Errorf("failed to scan result: %w", err)
	}

	return exists, nil
}

func randomDateRange() (time.Time, time.Time) {
	// Define the start and end of the initial date range.
	startDate := time.Date(1995, 1, 1, 0, 0, 0, 0, time.UTC)
	endDate := time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC)

	// Compute the total seconds between startDate and endDate.
	startUnix := startDate.Unix()
	endUnix := endDate.Unix()
	rangeDuration := endUnix - startUnix

	// Pick a random time between startDate and endDate.
	firstRandSec := startUnix + rand.Int64N(rangeDuration)
	firstDate := time.Unix(firstRandSec, 0)

	// Define the upper bound for the second date.
	maxEndDate := time.Date(2025, 2, 1, 0, 0, 0, 0, time.UTC)
	maxEndUnix := maxEndDate.Unix()

	// Ensure that the second date is between firstDate and maxEndDate.
	secondRangeDuration := maxEndUnix - firstRandSec
	secondRandSec := firstRandSec + rand.Int64N(secondRangeDuration)
	secondDate := time.Unix(secondRandSec, 0)

	return firstDate, secondDate
}
