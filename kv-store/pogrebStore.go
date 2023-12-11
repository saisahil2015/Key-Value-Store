
package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "os"

    "github.com/akrylysov/pogreb"
)

type KeyValueStore struct {
    db *pogreb.DB
}

func NewKeyValueStore(dbFile string) (*KeyValueStore, error) {
    db, err := pogreb.Open(dbFile, nil)
    if err != nil {
        return nil, err
    }
    return &KeyValueStore{db: db}, nil
}

func (kvs *KeyValueStore) Set(key, value string) error {

    return kvs.db.Put([]byte(key), []byte(value))
}

func (kvs *KeyValueStore) Get(key string) (string, bool, error) {
    val, err := kvs.db.Get([]byte(key))
    if err != nil {
		log.Fatal(err)
	}
	log.Printf("%s", val)
    return string(val), true, nil
}

func (kvs *KeyValueStore) Delete(key string) error {
    return kvs.db.Delete([]byte(key))
}

func HandleSet(kvs *KeyValueStore) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        var data map[string]string
        if err := json.NewDecoder(r.Body).Decode(&data); err != nil {
            http.Error(w, err.Error(), http.StatusBadRequest)
            return
        }
        for key, value := range data {
            if err := kvs.Set(key, value); err != nil {
                http.Error(w, err.Error(), http.StatusInternalServerError)
                return
            }
        }
        w.WriteHeader(http.StatusOK)
    }
}

func HandleGet(kvs *KeyValueStore) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        key := r.URL.Query().Get("key")
        value, exists, err := kvs.Get(key)
        if err != nil {
            http.Error(w, err.Error(), http.StatusInternalServerError)
            return
        }
        if !exists {
            http.Error(w, "Key not found", http.StatusNotFound)
            return
        }
        fmt.Fprint(w, value)
    }
}

func main() {
    if len(os.Args) < 3 {
        log.Fatal("Usage: go run kv_store.go [port] [db_file]")
    }
    port := os.Args[1]
    dbFile := os.Args[2]

    kvs, err := NewKeyValueStore(dbFile)
    if err != nil {
        log.Fatal(err)
    }
    defer kvs.db.Close()

    http.HandleFunc("/store", HandleSet(kvs))
    http.HandleFunc("/retrieve", HandleGet(kvs))

    fmt.Printf("Key-Value Store Server listening on :%s...\n", port)
    log.Fatal(http.ListenAndServe(":"+port, nil))
}




// go run pogrebStore.go 8070 db1.pogreb
// go run pogrebStore.go 8080 db2.pogreb
// go run pogrebStore.go 8090 db3.pogreb
