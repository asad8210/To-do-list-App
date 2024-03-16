from flask import Flask, request, session, redirect, jsonify
from flask_graphql import GraphQLView
import graphene
from keycloak import KeycloakOpenID
import stripe

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Set a secret key for session management

# Initialize Keycloak client
keycloak_openid = KeycloakOpenID(server_url="KEYCLOAK_SERVER_URL",
                                 client_id="YOUR_CLIENT_ID",
                                 realm_name="YOUR_REALM_NAME",
                                 client_secret_key="YOUR_CLIENT_SECRET_KEY",
                                 verify=True)

# Initialize Stripe
stripe.api_key = "sk_test_your_test_secret_key"  # Replace with your test secret key

# Dummy data for demonstration
todo_list = []

# GraphQL schema
class Todo(graphene.ObjectType):
    id = graphene.Int()
    title = graphene.String()
    description = graphene.String()
    time = graphene.String()
    images = graphene.List(graphene.String)

class Query(graphene.ObjectType):
    todos = graphene.List(Todo)

    def resolve_todos(self, info):
        # Check if user is authenticated
        if 'token' not in session:
            return None  # If not authenticated, return None
        return todo_list

class CreateTodo(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String(required=True)
        time = graphene.String(required=True)
        images = graphene.List(graphene.String)

    todo = graphene.Field(Todo)

    def mutate(self, info, title, description, time, images=[]):
        # Check if user is authenticated
        if 'token' not in session:
            return None  # If not authenticated, return None

        # Check if user has Pro license
        if 'pro_license' not in session:
            if not session.get('pro_license', False):
                return None  # If not a Pro user, return None

        new_todo = {'id': len(todo_list) + 1, 'title': title, 'description': description, 'time': time, 'images': images}
        todo_list.append(new_todo)
        return CreateTodo(todo=new_todo)

class DeleteTodo(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        # Check if user is authenticated
        if 'token' not in session:
            return None  # If not authenticated, return None

        global todo_list
        todo_list = [todo for todo in todo_list if todo['id'] != id]
        return DeleteTodo(success=True)

class EditTodo(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        description = graphene.String()
        time = graphene.String()
        images = graphene.List(graphene.String)

    todo = graphene.Field(Todo)

    def mutate(self, info, id, title=None, description=None, time=None, images=None):
        # Check if user is authenticated
        if 'token' not in session:
            return None  # If not authenticated, return None

        global todo_list
        for todo in todo_list:
            if todo['id'] == id:
                if title:
                    todo['title'] = title
                if description:
                    todo['description'] = description
                if time:
                    todo['time'] = time
                if images is not None:
                    todo['images'] = images
                return EditTodo(todo=todo)
        return EditTodo(todo=None)

class Mutation(graphene.ObjectType):
    create_todo = CreateTodo.Field()
    delete_todo = DeleteTodo.Field()
    edit_todo = EditTodo.Field()

    # Mutation for purchasing a Pro license
    purchase_pro_license = graphene.Boolean(success=graphene.Boolean())

    def resolve_purchase_pro_license(self, info):
        # Check if user is authenticated
        if 'token' not in session:
            return False  # If not authenticated, return False

        # Charge the user using Stripe
        try:
            # Create a Stripe Payment Intent
            intent = stripe.PaymentIntent.create(
                amount=1000,  # Amount in cents ($10.00)
                currency='usd',
                description='Pro License Purchase',
                payment_method_types=['card'],
                customer='CUSTOMER_ID'  # Replace with your customer ID or remove if not using customer setup
            )
            # Set the user's Pro license status in session
            session['pro_license'] = True
            return True  # Success
        except stripe.error.StripeError as e:
            return False  # Error during payment

schema = graphene.Schema(query=Query, mutation=Mutation)

# GraphQL endpoint
@app.route('/graphql', methods=['GET', 'POST'])
def graphql():
    # Check if user is authenticated
    if 'token' not in session:
        return redirect('/login')

    return GraphQLView.as_view('graphql', schema=schema, graphiql=True)(request)

# Login route
@app.route('/login')
def login():
    return redirect(keycloak_openid.auth_url("REDIRECT_URL"))

# Callback route after login
@app.route('/callback')
def callback():
    code = request.args.get('code')
    token = keycloak_openid.token(code)
    # Save the token in the session for future requests
    session['token'] = token
    return redirect('/graphql')  # Redirect to the GraphQL endpoint after successful login

if __name__ == '__main__':
    app.run(debug=True)

#Ensure that you replace "KEYCLOAK_SERVER_URL", "YOUR_CLIENT_ID", "YOUR_REALM_NAME", and "YOUR_CLIENT_SECRET_KEY" with your Keycloak server URL, client ID, realm name, and client secret key respectively.
