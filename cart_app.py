# Simple flask app with 3 hard-coded products, allowing you to add to the cart, 
# view the cart and clear the cart. The cart is stored in the session
# see the session["cart"] below
"""
If the user selcts the below, the correspondign session will be:

Add T-shirt once (product ID = 1)
Add Sneakers twice (product ID = 3)

session = {
    'cart': {
        '1': 1,  # 1 T-shirt
        '3': 2   # 2 Sneakers
    }
}
"""

from flask import Flask, render_template, redirect, url_for, session, request

app = Flask(__name__)
app.secret_key = 'secret'  # MUST have a secret key for session management

# Hard-coded products (you would have these in your database!)
products = [
    {'id': 1, 'name': 'T-shirt', 'price': 20},
    {'id': 2, 'name': 'Jeans', 'price': 40},
    {'id': 3, 'name': 'Sneakers', 'price': 60} ]

@app.route("/")
def home():            # EXAMPLE USING BOOTSTRAP LIBRARY
    return render_template('boot_products.html', products=products)



@app.route("/add_to_cart/<int:product_id>")   # Add to cart by product_id
def add_to_cart(product_id):

    cart = session.get("cart", {})
    # IMPORTANT Get the current cart from the session.
    #If there is no cart yet, use an empty dictionary {}.

    product_id_str = str(product_id)  # Convert to string

    if product_id_str in cart:
        cart[product_id_str] += 1     # Increase quantity
    else:
        cart[product_id_str] = 1      # First time, set quantity to 1


    # IMPORTANT - Convert product_id to a string (because session keys are strings).  
    # If the product is already in the cart, increase the quantity by 1.
    # If not, start with 0 and add 1.


    session["cart"] = cart
    # Save the updated cart back into the session.

    return redirect(url_for("view_cart"))


@app.route("/remove/<int:product_id>")   # Remove from cart by product_id
def remove_from_cart(product_id):

    cart = session.get("cart", {})  # Get the cart from the session
    cart.pop(str(product_id), None) # Remove a product from the cart
    session["cart"] = cart          # Save the updated cart back into the session.

    return redirect(url_for("view_cart"))


@app.route("/cart")                 # View the shopping cart            
def view_cart():

    cart = session.get("cart", {})
    cart_items = []
    total = 0

    for pid, qty in cart.items(): # For each product in the cart 

        # Find the first product in the products list whose id matches this pid from the cart
        
        # Convert the product ID from string to int
        pid_int = int(pid)

        # Set a default value in case no product is found
        product = None

        # Loop through each product in the list
        for p in products:
            if p['id'] == pid_int:
                product = p
                break  # Stop once we've found the match

        if product:         # We have a product
            subtotal = product['price'] * qty
            total += subtotal                    # Need to 'total' for the number of the same product in the cart

            cart_items.append({
                'product': product,
                'quantity': qty,
                'subtotal': subtotal
            })
    
    return render_template("simple_cart.html", cart_items=cart_items, total=total)


if __name__ == "__main__":
    app.run(debug=True)