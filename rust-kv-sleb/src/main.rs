use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use sled::Db;
use tokio::sync::Mutex;

#[derive(Debug, Serialize, Deserialize)]
struct KeyValue {
    value: String,
}

struct AppState {
    db: Mutex<Db>,
}

async fn get_key(data: web::Data<AppState>, path: web::Path<String>) -> impl Responder {
    let key = path.into_inner();
    let db = data.db.lock().await;

    if let Ok(Some(value)) = db.get(key.clone()) {
        HttpResponse::Ok().json(format!(
            "Key found, Value: {}",
            String::from_utf8_lossy(&value)
        ))
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

    let db = data.db.lock().await;
    let value_bytes: &[u8] = value.as_bytes();

    if db.contains_key(key.clone()).unwrap_or(false) {
        return HttpResponse::Conflict().json("Key already exists");
    }

    db.insert(key.clone(), value_bytes).unwrap();
    HttpResponse::Ok().json(format!("Key: {} set to value: {}", key, value))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let db1 = sled::open("my_db1").unwrap();
    let app_state1 = web::Data::new(AppState {
        db: Mutex::new(db1),
    });
    let server1 = HttpServer::new(move || {
        App::new()
            .app_data(app_state1.clone())
            .route("/get/{key}", web::get().to(get_key))
            .route("/set/{key}", web::put().to(set_key))
    })
    .bind("127.0.0.1:8080")?;

    let db2 = sled::open("my_db2").unwrap();
    let app_state2 = web::Data::new(AppState {
        db: Mutex::new(db2),
    });
    let server2 = HttpServer::new(move || {
        App::new()
            .app_data(app_state2.clone())
            .route("/get/{key}", web::get().to(get_key))
            .route("/set/{key}", web::put().to(set_key))
    })
    .bind("127.0.0.1:8081")?;

    let db3 = sled::open("my_db3").unwrap();
    let app_state3 = web::Data::new(AppState {
        db: Mutex::new(db3),
    });
    let server3 = HttpServer::new(move || {
        App::new()
            .app_data(app_state3.clone())
            .route("/get/{key}", web::get().to(get_key))
            .route("/set/{key}", web::put().to(set_key))
    })
    .bind("127.0.0.1:8082")?;

    futures::try_join!(server1.run(), server2.run(), server3.run())?;
    Ok(())
}
