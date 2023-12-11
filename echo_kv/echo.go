package main

import (
   "net/http"
   "github.com/labstack/echo/v4"
)

var keyValueStore = make(map[string]string)

func getValue(c echo.Context) error {
   key := c.Param("key")

   value := keyValueStore[key]
   return c.String(http.StatusOK, value)
}

func setValue(c echo.Context) error {
   req := new(struct {
      Key   string `json:"key"`
      Value string `json:"value"`
   })

   if err := c.Bind(req); err != nil {
      return err
   }

   keyValueStore[req.Key] = req.Value
   return c.String(http.StatusCreated, "OK")
}

func main() {
   e := echo.New()

   // Routes
   e.GET("/retrieve/:key", getValue)
   e.POST("/store/:key", setValue)

   // Start server
   e.Start(":8080")
}
