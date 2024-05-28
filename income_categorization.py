# Import the triangular_sigmoid function from the fuzzylogic library
from fuzzylogic.functions import triangular_sigmoid

# Define a function to determine the membership of an income value in different income categories
def income_membership(income):
    
    # Define membership functions for income categories using triangular_sigmoid
    high_income = triangular_sigmoid(70000, 149132)  # Example income ranges for high income
    medium_income = triangular_sigmoid(50000, 89744)  # Example income ranges for medium income
    low_income = triangular_sigmoid(0, 55000)  # Example income ranges for low income
    
    # Calculate membership degrees for each income category
    membership_high = high_income(income)
    membership_medium = medium_income(income)
    membership_low = low_income(income)
    
    # Create a dictionary to store the percentages of income belonging to each category
    membership_dict = {
        'high': membership_high,
        'medium': membership_medium,
        'low': membership_low
    }
    
    # Return the dictionary
    return membership_dict

# Example usage
income_value = 5000  # Example income value
income_dict = income_membership(income_value)  # Determine the membership of the income value
print("Membership INCOME:")
print(income_dict)  # Print the dictionary showing the percentages of income belonging to each category
best_income_category = max(income_dict, key=income_dict.get)
print("Best Income Category:", best_income_category)


def goal_membership(total_savings, target_amount):
    """
    Calculate the membership degrees for the goal based on the total savings and target amount.

    Args:
    - total_savings (float): Total savings accumulated for the goal until the present moment.
    - target_amount (float): Target amount for the goal.

    Returns:
    - dict: A dictionary containing the membership degrees for high, medium, and low progress towards the goal.
    """
    # Calculate the progress towards the goal
    progress = total_savings / target_amount

    # Define the ranges for high, medium, and low progress towards the goal
    high_progress_range = (0.8, 1)  # Adjusted for high progress
    medium_progress_range = (0.5, 0.8)  # Adjusted for medium progress
    low_progress_range = (0, 0.5)  # Adjusted for low progress

    # Calculate membership degrees for high, medium, and low progress towards the goal
    high_progress_membership = triangular_sigmoid(*high_progress_range)
    medium_progress_membership = triangular_sigmoid(*medium_progress_range)
    low_progress_membership = triangular_sigmoid(*low_progress_range)

    membership_high = high_progress_membership(progress)
    membership_medium = medium_progress_membership(progress)
    membership_low = low_progress_membership(progress)

    # Create a dictionary to store the percentages of progress towards the goal belonging to each category
    membership_dict = {
        'high': membership_high,
        'medium': membership_medium,
        'low': membership_low
    }

    return membership_dict

# Define the total savings and target amount for the goal
total_savings = 30000
target_amount = 60000

# Call the goal_membership function to calculate the membership degrees
membership_degrees = goal_membership(total_savings, target_amount)
# print(membership_degrees)

# # Print the membership degrees for high, medium, and low progress
# print("Membership Degrees:")
# print("High Progress:", membership_degrees['high'])
# print("Medium Progress:", membership_degrees['medium'])
# print("Low Progress:", membership_degrees['low'])