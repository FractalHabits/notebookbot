def get_api_key_choice(remaining_keys: set) -> str:
    """Get user choice for which API key to enter."""
    key_list = sorted(list(remaining_keys))
    
    for i, key in enumerate(key_list, 1):
        print(f"Do you want to enter your {key} ({i})? (yes/no/number) ", end='')
        choice = input().strip().lower()
        
        # Accept yes/y, the number, or the key name
        if choice in ('yes', 'y') or choice == str(i) or choice == key.lower():
            return key
            
        if choice in ('no', 'n'):
            continue
            
        print("Invalid choice. Please try again.")
    
    return None
