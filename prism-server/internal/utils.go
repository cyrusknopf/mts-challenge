package internal

import "fmt"

func ValidateApiKey(api_key string, db *Database) (bool, error) {
	q := `SELECT * FROM teams WHERE api_key ILIKE %s;`
	q = fmt.Sprint(q, api_key)
	rows, err := db.Query(q)
	if err != nil {
		return false, err
	}
	// Next returns false if there is no such row, true otherwise
	// FIXME: Probably a better way
	exists := rows.Next()
	return exists, err
}
