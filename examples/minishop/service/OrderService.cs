// MiniShop Service Layer
// C# Business Logic

using System;
using System.Collections.Generic;
using System.Data.SqlClient;

public class OrderService
{
    private string connectionString = "Server=localhost;Database=minishop;User Id=user;Password=password;";
    
    // Database operations
    public Order CreateOrder(Order order)
    {
        using (var connection = new SqlConnection(connectionString))
        {
            connection.Open();
            using (var command = new SqlCommand())
            {
                command.Connection = connection;
                command.CommandText = "INSERT INTO orders (user_id, product_id, quantity, total) VALUES (@userId, @productId, @quantity, @total)";
                command.Parameters.AddWithValue("@userId", order.UserId);
                command.Parameters.AddWithValue("@productId", order.ProductId);
                command.Parameters.AddWithValue("@quantity", order.Quantity);
                command.Parameters.AddWithValue("@total", order.Total);
                
                command.ExecuteNonQuery();
            }
        }
        
        // Emit event for order creation
        EmitEvent("OrderCreated", order.Id);
        
        return order;
    }
    
    public List<Order> GetOrdersByUser(int userId)
    {
        var orders = new List<Order>();
        
        using (var connection = new SqlConnection(connectionString))
        {
            connection.Open();
            using (var command = new SqlCommand())
            {
                command.Connection = connection;
                command.CommandText = "SELECT * FROM orders WHERE user_id = @userId";
                command.Parameters.AddWithValue("@userId", userId);
                
                using (var reader = command.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        orders.Add(new Order
                        {
                            Id = (int)reader["id"],
                            UserId = (int)reader["user_id"],
                            ProductId = (int)reader["product_id"],
                            Quantity = (int)reader["quantity"],
                            Total = (decimal)reader["total"]
                        });
                    }
                }
            }
        }
        
        return orders;
    }
    
    // Calls external API
    public PaymentResult ProcessPayment(PaymentRequest request)
    {
        // This would call external payment API
        var httpClient = new System.Net.Http.HttpClient();
        var json = System.Text.Json.JsonSerializer.Serialize(request);
        var content = new System.Net.Http.StringContent(json, System.Text.Encoding.UTF8, "application/json");
        var response = httpClient.PostAsync("https://payment-api.example.com/charge", content).Result;
        var result = System.Text.Json.JsonSerializer.Deserialize<PaymentResult>(response.Content.ReadAsStringAsync().Result);
        
        return result;
    }
    
    private void EmitEvent(string eventName, object data)
    {
        // Event emission logic
        Console.WriteLine($"Event: {eventName}, Data: {data}");
    }
}

public class Order
{
    public int Id { get; set; }
    public int UserId { get; set; }
    public int ProductId { get; set; }
    public int Quantity { get; set; }
    public decimal Total { get; set; }
}

public class PaymentRequest
{
    public decimal Amount { get; set; }
    public string CardToken { get; set; }
}

public class PaymentResult
{
    public bool Success { get; set; }
    public string TransactionId { get; set; }
    public string Message { get; set; }
}
