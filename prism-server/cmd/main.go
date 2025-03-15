package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"

	"mtschal/internal"
)

const (
	defaultPort    = 8082
	defaultAddress = "0.0.0.0"
)

func main() {
	// Define command-line flags for address and port.
	addr := flag.String("addr", defaultAddress, "Server address to bind to")
	port := flag.Int("port", defaultPort, "Server port to listen on")
	flag.Parse()

	http.HandleFunc("/submit", internal.PostHandler)
	log.Printf("Starting server on port %d", *port)

	net := fmt.Sprintf("%s:%d", *addr, *port)
	if err := http.ListenAndServe(net, nil); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}
