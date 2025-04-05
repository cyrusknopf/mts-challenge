package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"time"

	"mtschal/internal"
)

const (
	defaultPort             = 8082
	defaultAddress          = "0.0.0.0"
	defaultEvaluationDir    = "/workspace/eval"
	defaultPostgresUser     = "postgres"
	defaultPostgresAddress  = "postgresql"
	defaultPostgresPort     = 5432
	defaultPostgresDatabase = "prism"
	defaultTTL              = 10
	defaultNumLLMServers    = 3
)

func main() {
	ttl := flag.Int("ttl", defaultTTL, fmt.Sprintf("Time to live, default %d", defaultTTL))
	addr := flag.String("addr", defaultAddress, "Server address to bind to")
	port := flag.Int("port", defaultPort, "Server port to listen on")
	paddr := flag.String("paddr", defaultPostgresAddress, "Postgres address")
	pport := flag.Int("pport", defaultPostgresPort, "Postgres port")
	pdb := flag.String("pdb", defaultPostgresDatabase, "Postgres database name")
	puser := flag.String("puser", defaultPostgresUser, "Postgres username")
	ppwd := flag.String("ppwd", "", "Postgres password")
	apikey := flag.String("apikey", "", "Api key for polygon")
	evalDir := flag.String("eval-dir", defaultEvaluationDir, "Evaluation directory path")
	numLLMServer := flag.Int("numLLMServer", defaultNumLLMServers, "Number of LLM servers stood up")
	flag.Parse()

	// Establish connection to a known postgres server.
	db := internal.NewDatabase(*paddr, *pport, *puser, *pdb)
	err := db.Connect(*ppwd)
	if err != nil {
		fmt.Printf("Error unable to connect to postgres database: %v\n", err)
		return
	}

	// Map API keys to contexts from requests
	userContext := make(map[string]*internal.RequestContext)

	handlers := internal.NewHandlers(&db, userContext, time.Duration(*ttl)*time.Second, *evalDir, *apikey, *numLLMServer)

	// HTTP Handler for client answers.
	http.HandleFunc("/submit", handlers.PostHandler)
	http.HandleFunc("/request", handlers.GetHandler)
	http.HandleFunc("/info", handlers.InfoHandler)
	log.Printf("Starting server on port %d", *port)
	net := fmt.Sprintf("%s:%d", *addr, *port)
	if err := http.ListenAndServe(net, nil); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}
