import requests
from keycloak import KeycloakOpenID

def perform_graphql_operations():
    # Initialize Keycloak client
    keycloak_openid = KeycloakOpenID(server_url="KEYCLOAK_SERVER_URL",
                                     client_id="YOUR_CLIENT_ID",
                                     realm_name="YOUR_REALM_NAME",
                                     client_secret_key="YOUR_CLIENT_SECRET_KEY",
                                     verify=True)

    # Get Keycloak login URL
    login_url = keycloak_openid.auth_url("REDIRECT_URL")

    # Open login URL in browser for user authentication
    print("Please log in with Keycloak:")
    print(login_url)
    # After successful login, the user will be redirected to the redirect URL
    redirect_url = input("Enter the redirect URL: ")

    # Extract authorization code from the redirect URL
    authorization_code = keycloak_openid.code_from_url(redirect_url)

    # Exchange authorization code for access token
    token = keycloak_openid.token(authorization_code)

    # Get GraphQL endpoint URL
    graphql_url = 'http://localhost:5000/graphql'  # Update with your GraphQL endpoint URL

    # GraphQL query for listing all To-Dos
    query_list_todos = """
        query {
            todos {
                id
                title
                description
                time
                images
            }
        }
    """

    # Send the query with access token as Authorization header
    headers = {'Authorization': f'Bearer {token["access_token"]}'}
    response = requests.post(graphql_url, json={'query': query_list_todos}, headers=headers)
    print("Response from listing To-Dos:")
    print(response.json())

    # Define variables for creating a ToDo
    variables_create_todo = {
        'title': 'Complete Python project',
        'description': 'Finish the Python project with all the required features.',
        'time': 'ASAP',
        'images': ['image1.jpg', 'image2.jpg']
    }

    # GraphQL mutation for creating a ToDo
    mutation_create_todo = """
        mutation CreateTodo($title: String!, $description: String!, $time: String!, $images: [String]) {
            create_todo(title: $title, description: $description, time: $time, images: $images) {
                todo {
                    id
                    title
                    description
                    time
                    images
                }
            }
        }
    """

    # Send the mutation to create a ToDo with access token as Authorization header
    response = requests.post(graphql_url, json={'query': mutation_create_todo, 'variables': variables_create_todo}, headers=headers)
    print("\nResponse from creating a ToDo:")
    print(response.json())

    # Define variables for deleting a ToDo
    variables_delete_todo = {
        'id': 1  # Replace with the ID of the ToDo you want to delete
    }

    # GraphQL mutation for deleting a ToDo
    mutation_delete_todo = """
        mutation DeleteTodo($id: Int!) {
            delete_todo(id: $id) {
                success
            }
        }
    """

    # Send the mutation to delete a ToDo with access token as Authorization header
    response = requests.post(graphql_url, json={'query': mutation_delete_todo, 'variables': variables_delete_todo}, headers=headers)
    print("\nResponse from deleting a ToDo:")
    print(response.json())

    # Define variables for editing a ToDo
    variables_edit_todo = {
        'id': 2,  # Replace with the ID of the ToDo you want to edit
        'title': 'Updated Title',
        'description': 'Updated Description',
        'time': 'Updated Time',
        'images': ['updated_image1.jpg', 'updated_image2.jpg']
    }

    # GraphQL mutation for editing a ToDo
    mutation_edit_todo = """
        mutation EditTodo($id: Int!, $title: String, $description: String, $time: String, $images: [String]) {
            edit_todo(id: $id, title: $title, description: $description, time: $time, images: $images) {
                todo {
                    id
                    title
                    description
                    time
                    images
                }
            }
        }
    """

    # Send the mutation to edit a ToDo with access token as Authorization header
    response = requests.post(graphql_url, json={'query': mutation_edit_todo, 'variables': variables_edit_todo}, headers=headers)
    print("\nResponse from editing a ToDo:")
    print(response.json())

if __name__ == "__main__":
    perform_graphql_operations()
