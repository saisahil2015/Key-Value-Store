package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"sync"
	"os"
	"log"
)

// KeyValueStore represents a basic key-value store.
type KeyValueStore struct {
	mu    sync.RWMutex
	store map[string]string
}

// NewKeyValueStore creates a new instance of KeyValueStore.
func NewKeyValueStore() *KeyValueStore {
	return &KeyValueStore{
		store: make(map[string]string),
	}
}

// Set adds or updates a key-value pair in the store.
func (kvs *KeyValueStore) Set(key, value string) {
	kvs.mu.Lock()
	defer kvs.mu.Unlock()
	kvs.store[key] = value
}


// Get retrieves the value associated with a key.
func (kvs *KeyValueStore) Get(key string) (string, bool) {
	kvs.mu.RLock()
	defer kvs.mu.RUnlock()
	value, exists := kvs.store[key]
	return value, exists
}

// Delete removes a key-value pair from the store.
func (kvs *KeyValueStore) Delete(key string) {
	kvs.mu.Lock()
	defer kvs.mu.Unlock()
	delete(kvs.store, key)
}

// HandleSet handles HTTP requests to set a key-value pair.
func HandleSet(kvs *KeyValueStore) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var data map[string]string
		if err := json.NewDecoder(r.Body).Decode(&data); err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}

        //fmt.Print("data: ", data, "\n")
		for key, value := range data {
			kvs.Set(key, value)
            /*fmt.Print("Name: ", key, "\n")
            
            fmt.Print("value: ", value, "\n")
        
            fmt.Print("kvs stores: ", kvs.store[key], "\n")*/
		}
        
        w.Header().Set("Content-Type", "text/plain")
        fmt.Fprint(w, '1')
		//w.WriteHeader(http.StatusOK)
	}
}


// HandleGet handles HTTP requests to get a value by key.
func HandleGet(kvs *KeyValueStore) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		key := r.URL.Query().Get("key")
        //fmt.Print("GET request key: ", key, "\n")
		value, exists := kvs.Get(key)
		if !exists {
			http.Error(w, "0", http.StatusNotFound)
			return
		}

		//response := map[string]string{"key": key, "value": value}
        //fmt.Print("GET response: ", value, "\n")
		//jsonResponse, err := json.Marshal(response)
        /*
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}*/

        w.Header().Set("Content-Type", "text/plain")
        fmt.Fprint(w, value)
		//w.Header().Set("Content-Type", "application/json")
		//w.Write(jsonResponse)
	}
}

// HandleDelete handles HTTP requests to delete a key-value pair.
func HandleDelete(kvs *KeyValueStore) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		key := r.URL.Query().Get("key")
		kvs.Delete(key)

		w.WriteHeader(http.StatusOK)
	}
}

func main() {
    if len(os.Args) < 2 {
        log.Fatal("Usage: go run kv_store.go [port]")
    }
    port := os.Args[1]

    kvs := NewKeyValueStore()

    http.HandleFunc("/store", HandleSet(kvs))
    http.HandleFunc("/retrieve", HandleGet(kvs))
    http.HandleFunc("/remove", HandleDelete(kvs))

    fmt.Printf("Key-Value Store Server listening on :%s...\n", port)
    log.Fatal(http.ListenAndServe(":"+port, nil))
}