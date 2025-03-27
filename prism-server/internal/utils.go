package internal

import "fmt"

func ValidateApiKey(api_key string, db *Database) (bool, error) {
	var exists bool
	query := `SELECT EXISTS(SELECT 1 FROM teams WHERE api_key = $1);`

	// Safely pass api_key as a parameter
	row, err := db.QueryRow(query, api_key)
	if err != nil {
		return false, err
	}

	// Now scan the row result
	err = row.Scan(&exists)
	if err != nil {
		return false, fmt.Errorf("failed to scan result: %w", err)
	}

	return exists, nil
}
