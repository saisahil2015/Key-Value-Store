package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "os"
    "sync"
    "time"
)

type KeyValueStore struct {
    mu          sync.RWMutex
    store       map[string]string
    writeQueue  []func()
    writeMutex  sync.Mutex
}

func NewKeyValueStore() *KeyValueStore {
    return &KeyValueStore{
        store:      make(map[string]string),
        writeQueue: make([]func(), 0),
    }
}

func (kvs *KeyValueStore) QueueSet(key, value string) {
    kvs.writeMutex.Lock()
    kvs.writeQueue = append(kvs.writeQueue, func() {
        kvs.mu.Lock()
        kvs.store[key] = value
        kvs.mu.Unlock()
    })
    kvs.writeMutex.Unlock()
}

func (kvs *KeyValueStore) Get(key string) (string, bool) {
    kvs.mu.RLock()
    defer kvs.mu.RUnlock()
    value, exists := kvs.store[key]
    return value, exists
}

// func (kvs *KeyValueStore) processWriteQueue() {
//     kvs.writeMutex.Lock()
//     for _, writeOp := range kvs.writeQueue {
//         writeOp()
//     }
//     kvs.writeQueue = make([]func(), 0)
//     kvs.writeMutex.Unlock()
// }

func (kvs *KeyValueStore) processWriteQueue() {
    kvs.writeMutex.Lock()
    numWrites := len(kvs.writeQueue)
    for _, writeOp := range kvs.writeQueue {
        writeOp()
    }
    kvs.writeQueue = make([]func(), 0)
    kvs.writeMutex.Unlock()

    if numWrites > 0 {
        fmt.Printf("Processed %d write requests in batch\n", numWrites)
    }
}


func HandleSet(kvs *KeyValueStore) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        var data map[string]string
        if err := json.NewDecoder(r.Body).Decode(&data); err != nil {
            http.Error(w, err.Error(), http.StatusBadRequest)
            return
        }
        for key, value := range data {
            kvs.QueueSet(key, value)
        }
        w.WriteHeader(http.StatusOK)
    }
}

func HandleGet(kvs *KeyValueStore) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        key := r.URL.Query().Get("key")
        value, exists := kvs.Get(key)
        if !exists {
            http.Error(w, "Key not found", http.StatusNotFound)
            return
        }
        fmt.Fprint(w, value)
    }
}

func main() {
    if len(os.Args) < 2 {
        log.Fatal("Usage: go run kv_store.go [port]")
    }
    port := os.Args[1]

    kvs := NewKeyValueStore()

    go func() {
        ticker := time.NewTicker(400 * time.Millisecond)
        for range ticker.C {
            kvs.processWriteQueue()
        }
    }()

    http.HandleFunc("/store", HandleSet(kvs))
    http.HandleFunc("/retrieve", HandleGet(kvs))

    fmt.Printf("Server listening on :%s...\n", port)
    log.Fatal(http.ListenAndServe(":"+port, nil))
}

