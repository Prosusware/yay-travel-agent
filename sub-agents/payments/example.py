"""
Example usage of the refactored BookingAgent class
Demonstrates how to use the class-based booking agent with specialized prompts
"""

from app.services.booking_agent import BookingAgent
import asyncio


async def example_single_booking():
    """Example of booking a single flight using the new BookingAgent class."""
    async with BookingAgent() as agent:
        result = await agent.book_flight(
            initial_url="https://flights.booking.com",
            departure="London, UK",
            destination="Paris, France",
            departure_date="August 1st, 2025",
            return_date="August 15th, 2025",
            budget="500 GBP",
            traveler_info={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "address": "123 Main St",
                "city": "Anytown",  
                "country": "USA"
            }
        )
        print("=== Flight Booking Result ===")
        print(result)


async def example_multiple_bookings():
    """Example of running multiple different types of bookings in sequence."""
    async with BookingAgent() as agent:
        # Book a flight
        flight_result = await agent.book_flight(
            initial_url="https://flights.booking.com",
            departure="London, UK",
            destination="Paris, France",
            departure_date="August 1st, 2025",
            return_date="August 15th, 2025",
            budget="500 GBP",
            traveler_info={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "address": "123 Main St",
                "city": "Anytown",  
                "country": "USA"
            }
        )
        print("=== Flight Booking Result ===")
        print(flight_result)
        
        # Book a hotel
        hotel_result = await agent.book_hotel(
            initial_url="https://www.booking.com/",
            city="Paris, France",
            location_preference="Near Louvre",    
            check_in_date="August 1st, 2025",
            check_out_date="August 5th, 2025",
            budget="1000 GBP total",
            num_guests=2,
            traveler_info={
                "first_name": "Jane",       
                "last_name": "Smith",
                "email": "jane.smith@example.com",
                "phone": "+1987654321",
                "address": "456 Oak Ave",
                "city": "Somewhere",
                "country": "USA"    
            }
        )
        print("\n=== Hotel Booking Result ===")
        print(hotel_result)
        
        # Order food delivery
        food_result = await agent.order_food_delivery(
            cuisine="Italian",
            dishes=["Margherita Pizza", "Caesar Salad"],
            delivery_address="Rue de Rivoli, 75001 Paris, France",  
            max_eta="45 minutes",
            budget="30 EUR",
            delivery_info={
                "first_name": "Mike",
                "last_name": "Johnson",
                "email": "mike.johnson@example.com",            
                "phone": "+1555123456",
                "address": "789 Pine St",
                "city": "Downtown",
                "country": "USA"
            }
        )
        print("\n=== Food Delivery Result ===")
        print(food_result)


async def example_parallel_bookings():
    """Example of running multiple bookings in parallel (not recommended)."""
    # Note: This approach is not recommended as it shares the same browser
    # session which can cause conflicts. Use sequential booking instead.
    async with BookingAgent() as agent:
        # Create tasks for parallel execution
        tasks = [
            agent.book_flight(
                initial_url="https://flights.booking.com",
                departure="London, UK",
                destination="Paris, France",
                departure_date="August 1st, 2025",
                return_date="August 15th, 2025",
                budget="500 GBP",
                traveler_info={
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "phone": "+1234567890",
                    "address": "123 Main St",
                    "city": "Anytown",  
                    "country": "USA"
                }
            ),
            agent.book_hotel(
                initial_url="https://www.booking.com/",
                city="Paris, France",
                location_preference="Near Louvre",    
                check_in_date="August 1st, 2025",
                check_out_date="August 5th, 2025",
                budget="1000 GBP total",
                num_guests=2,
                traveler_info={
                    "first_name": "Jane",       
                    "last_name": "Smith",
                    "email": "jane.smith@example.com",
                    "phone": "+1987654321",
                    "address": "456 Oak Ave",
                    "city": "Somewhere",
                    "country": "USA"    
                }
            ),
            agent.order_food_delivery(
                cuisine="Italian",
                dishes=["Margherita Pizza", "Caesar Salad"],
                delivery_address="Rue de Rivoli, 75001 Paris, France",  
                max_eta="45 minutes",
                budget="30 EUR",
                delivery_info={
                    "first_name": "Mike",
                    "last_name": "Johnson",
                    "email": "mike.johnson@example.com",            
                    "phone": "+1555123456",
                    "address": "789 Pine St",
                    "city": "Downtown",
                    "country": "USA"
                }
            )
        ]
        
        # Run all tasks in parallel
        results = await asyncio.gather(*tasks)
        
        # Print results
        for i, result in enumerate(results):
            booking_types = ["Flight", "Hotel", "Food Delivery"]
            print(f"\n=== {booking_types[i]} Booking Result ===")
            print(result)


async def main():
    """Main function to run examples."""
    print("Running single booking example...")
    await example_single_booking()
    
    # print("\n" + "="*50 + "\n")
    
    # print("Running multiple sequential bookings example...")
    # await example_multiple_bookings()
    
    # print("\n" + "="*50 + "\n")
    
    # print("Running parallel bookings example...")
    # await example_parallel_bookings()

if __name__ == "__main__":
    asyncio.run(main()) 