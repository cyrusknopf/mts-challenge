package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"

	"mtschal/internal"
)

const (
	defaultPort             = 8082
	defaultAddress          = "0.0.0.0"
	defaultPostgresUser     = "postgres"
	defaultPostgresAddress  = "postgresql"
	defaultPostgresPort     = 5432
	defaultPostgresDatabase = "prism"
)

func main() {
	addr := flag.String("addr", defaultAddress, "Server address to bind to")
	port := flag.Int("port", defaultPort, "Server port to listen on")
	paddr := flag.String("paddr", defaultPostgresAddress, "Postgres address")
	pport := flag.Int("pport", defaultPostgresPort, "Postgres port")
	pdb := flag.String("pdb", defaultPostgresDatabase, "Postgres database name")
	puser := flag.String("puser", defaultPostgresUser, "Postgres username")
	ppwd := flag.String("ppwd", "", "Postgres password")
	flag.Parse()

	// Establish connection to a known postgres server.
	db := internal.NewDatabase(*paddr, *pport, *puser, *pdb)
	err := db.Connect(*ppwd)
	if err != nil {
		fmt.Printf("Error unable to connect to postgres database: %v\n", err)
		return
	}

	// Map API keys to contexts from requests
	user_context := make(map[string]*internal.RequestContext)

	handlers := internal.NewHandlers(&db, user_context)

	// HTTP Handler for client answers.
	http.HandleFunc("/submit", handlers.PostHandler)
	http.HandleFunc("/request", handlers.GetHandler)
	log.Printf("Starting server on port %d", *port)
	net := fmt.Sprintf("%s:%d", *addr, *port)
	if err := http.ListenAndServe(net, nil); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}
