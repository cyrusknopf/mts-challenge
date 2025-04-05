package internal

import (
	"fmt"
	"maps"
	"math"
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

const (
	SEVEN_YEARS_IN_SECONDS int64 = 220752000
)

func GenerateRandomContext() RequestContext {
	timestamp := time.Now() // Reset later

	age := rand.IntN(MAX_AGE-MIN_AGE) + MIN_AGE

	salary := math.Round(math.Abs(rand.NormFloat64()*SALARY_STD + SALARY_MEAN))

	budget := math.Round(math.Abs(rand.NormFloat64()*BUDGET_STD+BUDGET_MEAN) * salary)

	// More likely to be employed than unemployed.
	employed := rand.IntN(8) != 0

	if !employed {
		// Force salary to 0, if unemployed. Still gives budget to invest.
		salary = 0.0
	}

	startDate, endDate := randomDateRange()

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

	ctx := RequestContext{
		Timestamp:        timestamp,
		StartDate:        startDate.Format("2006-01-02"),
		EndDate:          endDate.Format("2006-01-02"),
		Age:              age,
		EmploymentStatus: employed,
		Salary:           salary,
		Budget:           budget,
		Dislikes:         dislikes,
	}
	return ctx
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

	// Define the soft upper bound for the second date
	softEndUnix := firstRandSec + SEVEN_YEARS_IN_SECONDS

	// Define actual upper bound for second date
	boundEndUnix := min(maxEndUnix, softEndUnix)

	// Ensure that the second date is between firstDate and maxEndDate.
	secondRangeDuration := boundEndUnix - firstRandSec
	secondRandSec := firstRandSec + rand.Int64N(secondRangeDuration)
	secondDate := time.Unix(secondRandSec, 0)

	return firstDate, secondDate
}
