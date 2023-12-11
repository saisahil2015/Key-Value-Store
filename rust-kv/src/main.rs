use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use tokio::sync::Mutex;

#[derive(Debug, Serialize, Deserialize)]
struct KeyValue {
    value: String,
}

#[derive(Default)]
struct AppState {
    data: Mutex<HashMap<String, String>>,
}

async fn get_key(data: web::Data<AppState>, path: web::Path<String>) -> impl Responder {
    let key = path.into_inner();
    let data = data.data.lock().await;

    if let Some(value) = data.get(&key) {
        HttpResponse::Ok().json(format!("Key found, Value: {}", value))
    } else {
        HttpResponse::NotFound().json("Key not found")
    }
}

async fn set_key(
    data: web::Data<AppState>,
    path: web::Path<String>,
    form_data: web::Form<KeyValue>,
) -> impl Responder {
    let key = path.into_inner();
    let value = form_data.value.clone();

    let mut data = data.data.lock().await;

    if data.contains_key(&key) {
        return HttpResponse::Conflict().json("Key already exists");
    }

    data.insert(key.clone(), value.clone());
    HttpResponse::Ok().json(format!("Key: {} set to value: {}", key, value))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let app_state1 = web::Data::new(AppState::default());
    let server1 = HttpServer::new(move || {
        App::new()
            .app_data(app_state1.clone())
            .route("/get/{key}", web::get().to(get_key))
            .route("/set/{key}", web::put().to(set_key))
    })
    .bind("127.0.0.1:8080")?;
    println!("Starting server at: http://127.0.0.1:8080");

    let app_state2 = web::Data::new(AppState::default());
    let server2 = HttpServer::new(move || {
        App::new()
            .app_data(app_state2.clone())
            .route("/get/{key}", web::get().to(get_key))
            .route("/set/{key}", web::put().to(set_key))
    })
    .bind("127.0.0.1:8081")?;
    println!("Starting server at: http://127.0.0.1:8081");

    let app_state3 = web::Data::new(AppState::default());
    let server3 = HttpServer::new(move || {
        App::new()
            .app_data(app_state3.clone())
            .route("/get/{key}", web::get().to(get_key))
            .route("/set/{key}", web::put().to(set_key))
    })
    .bind("127.0.0.1:8082")?;
    println!("Starting server at: http://127.0.0.1:8082");

    futures::try_join!(server1.run(), server2.run(), server3.run())?;
    Ok(())
}
