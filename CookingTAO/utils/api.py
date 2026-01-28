import requests

def get_PE(api_url: str) -> float:
    """
    Get Platform Earning (PE) from the API.
    
    Arguments:
        api_url (str): The base URL of the API.
        
    Returns:
        float: The Platform Earning value.
    """
    try:
        response = requests.get(f"{api_url}/platform-earnings")
        response.raise_for_status()
        if not response.success:
            raise ValueError("Invalid response from API")
            
        data = response.data.platform_earning_in_rao
        return float(data)
    except requests.RequestException as e:
        raise RuntimeError(f"Error fetching Platform Earning: {e}")

def get_subnet_miner(api_url: str) -> dict:
    """
    Get subnet miners and their adopters.
    
    Arguments:
        api_url (str): The base URL of the API.
    
    Returns:
    {
        "Subnet Netuid 1": {
            "HK1": ["Adopters HK1", "Adopters HK2", ...],
            "HK2": ["Adopters HK1", "Adopters HK2", ...]
            ...
        },
        "Subnet Netuid 2": {
            ...
        }
    }
    """
    try:
        response = requests.get(f"{api_url}/miners")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Error fetching subnet miners: {e}")


def get_subnets(api_url: str) -> dict:
    """
    Get subnets and their importance factors.
    
    Arguments:
        api_url (str): The base URL of the API.
    
    Returns:
    {
        "Subnet Netuid 1": "Importance Factor",
        "Subnet Netuid 2": "Importance Factor",
        ...
    }
    """
    try:
        response = requests.get(f"{api_url}/subnets")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Error fetching subnets: {e}")