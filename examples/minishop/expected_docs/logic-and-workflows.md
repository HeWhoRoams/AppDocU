# MiniShop Logic & Workflows

## Order Creation Flow

### Sources → Inputs → Transformations → Outputs → Presentation

| Source | Inputs | Transformations | Outputs | Presentation |
|--------|--------|--------|----------------|---------|--------------|| API Endpoint `/api/orders` | JSON: `{user_id, product_id, quantity, amount, card_info}` | 1. Validates input data<br>2. Creates database connection<br>3. Inserts order record<br>4. Calls payment service<br>5. Commits transaction | 1. Database: `INSERT INTO orders`<br>2. API: `POST https://payment-api.example.com/charge`<br>3. Event: `OrderCreated` | JSON: `{order_id, payment_status}` |

### Evidence & Confidence
- **Evidence**: `api/app.py:25-40` - Order creation endpoint with DB write and API call
- **Confidence**: HIGH
- **Rationale**: Clear database INSERT and external API call pattern

## Product Retrieval Flow

### Sources → Inputs → Transformations → Outputs → Presentation

| Source | Inputs | Transformations | Outputs | Presentation |
|--------|--------|----------------|---------|--------------|
| API Endpoint `/api/products` | HTTP GET request | 1. Creates database connection<br>2. Executes SELECT query<br>3. Fetches all records | Database: `SELECT * FROM products` | JSON: Array of product objects |

### Evidence & Confidence
- **Evidence**: `api/app.py:15-23` - Product retrieval with database READ
- **Confidence**: HIGH
- **Rationale**: Clear database SELECT pattern

## Order Service Flow

### Sources → Inputs → Transformations → Outputs → Presentation

| Source | Inputs | Transformations | Outputs | Presentation |
|--------|----------------|---------|--------------|
| `OrderService.CreateOrder` | `Order` object with user, product, quantity, total | 1. Validates order data<br>2. Creates SQL connection<br>3. Executes INSERT statement<br>4. Emits OrderCreated event | 1. Database: `INSERT INTO orders`<br>2. Event: `OrderCreated`<br>3. API: `POST https://payment-api.example.com/charge` | Created `Order` object |

### Evidence & Confidence
- **Evidence**: `service/OrderService.cs:10-28` - Order creation with DB write and event emission
- **Confidence**: HIGH
- **Rationale**: Clear database operations and event pattern in C# code

## Payment Processing Flow

### Sources → Inputs → Transformations → Outputs → Presentation

| Source | Inputs | Transformations | Outputs | Presentation |
|--------|--------|----------------|---------|--------------|
| `OrderService.ProcessPayment` | `PaymentRequest` with amount and card token | 1. Serializes request to JSON<br>2. Makes HTTP POST to payment API<br>3. Deserializes response | API: `POST https://payment-api.example.com/charge` | `PaymentResult` with success status |

### Evidence & Confidence
- **Evidence**: `service/OrderService.cs:45-56` - Payment processing with external API call
- **Confidence**: HIGH
- **Rationale**: Clear HTTP client pattern for external API integration
