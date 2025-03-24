package internal

import (
	"database/sql"
	"fmt"

	_ "github.com/lib/pq"
)

type Database struct {
	addr     string
	port     int
	user     string
	database string
	conn     *sql.DB
}

func NewDatabase(addr string, port int, user string, database string) Database {
	return Database{
		addr, port, user, database, nil,
	}
}

func (db *Database) Connect(password string) error {
	connStr := fmt.Sprintf("dbname=%s host=%s user=%s port=%d password='%s' dbname=%s sslmode=disable", db.database, db.addr, db.user, db.port, password, db.database)
	conn, err := sql.Open("postgres", connStr)
	if err != nil {
		return err
	}
	db.conn = conn
	return nil
}

func (db *Database) Query(query string, args ...any) (*sql.Rows, error) {
	return db.conn.Query(query)
}

func (db *Database) QueryRow(query string, args ...any) (*sql.Row, error) {
	return db.conn.QueryRow(query), nil
}
