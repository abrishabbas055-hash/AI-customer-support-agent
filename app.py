"""
🤖 PRODUCTION LEVEL AI CUSTOMER SUPPORT AGENT
Features: Conversation Memory, Context Awareness, Step-by-Step Flow
"""

from flask import Flask, request, jsonify, render_template_string, session
from datetime import datetime
import re
import json
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-12345'

# ============================================
# CONVERSATION STATE MANAGEMENT
# ============================================
# Stores user conversation context
user_sessions = {}

# ============================================
# ORDER DATABASE
# ============================================
ORDER_DATABASE = {
    "ORD-12345": {
        "status": "Delivered",
        "date": "2024-01-15",
        "total": "$49.99",
        "product": "Wireless Headphones",
        "tracking": "TRK-987654321",
        "delivered_date": "2024-01-18"
    },
    "ORD-67890": {
        "status": "In Transit",
        "date": "2024-01-18",
        "total": "$129.99",
        "product": "Smart Watch",
        "tracking": "TRK-123456789",
        "expected_date": "2024-01-22"
    },
    "ORD-11111": {
        "status": "Processing",
        "date": "2024-01-20",
        "total": "$79.99",
        "product": "Bluetooth Speaker",
        "expected_date": "2024-01-24"
    }
}

# ============================================
# PRODUCT CATALOG
# ============================================
PRODUCTS = {
    "headphones": {"name": "Wireless Headphones", "price": "$49.99", "stock": "In Stock"},
    "smart watch": {"name": "Smart Watch", "price": "$129.99", "stock": "In Stock"},
    "speaker": {"name": "Bluetooth Speaker", "price": "$79.99", "stock": "Low Stock"}
}

# ============================================
# SUPPORT TICKETS
# ============================================
tickets = {}

# ============================================
# PRODUCTION BOT WITH CONTEXT
# ============================================
class ProductionBot:
    def __init__(self):
        self.states = {
            'idle': 'idle',
            'awaiting_order_number': 'awaiting_order_number',
            'awaiting_refund_details': 'awaiting_refund_details',
            'awaiting_product_name': 'awaiting_product_name',
            'awaiting_ticket_details': 'awaiting_ticket_details'
        }
    
    def get_or_create_session(self, user_id):
        if user_id not in user_sessions:
            user_sessions[user_id] = {
                'state': 'idle',
                'context': {},
                'history': [],
                'last_intent': None
            }
        return user_sessions[user_id]
    
    def process_message(self, message, user_id):
        session = self.get_or_create_session(user_id)
        message_lower = message.lower().strip()
        
        # Save to history
        session['history'].append({'role': 'user', 'message': message, 'time': datetime.now().isoformat()})
        
        # Check current state first
        current_state = session['state']
        
        # STATE: Awaiting Order Number
        if current_state == 'awaiting_order_number':
            return self.handle_order_number_provided(message, session, user_id)
        
        # STATE: Awaiting Refund Details
        if current_state == 'awaiting_refund_details':
            return self.handle_refund_details_provided(message, session, user_id)
        
        # STATE: Awaiting Product Name
        if current_state == 'awaiting_product_name':
            return self.handle_product_query(message, session, user_id)
        
        # STATE: Awaiting Ticket Details
        if current_state == 'awaiting_ticket_details':
            return self.handle_ticket_creation(message, session, user_id)
        
        # Check for order number in message (even in idle state)
        order_match = re.search(r'ORD-\d{5}', message.upper())
        if order_match:
            return self.handle_order_number_provided(message, session, user_id)
        
        # Intent detection for new queries
        if 'order status' in message_lower or 'track order' in message_lower or 'where is my order' in message_lower:
            session['state'] = 'awaiting_order_number'
            session['last_intent'] = 'order_status'
            return self.ask_for_order_number()
        
        elif 'refund' in message_lower or 'return' in message_lower:
            session['state'] = 'awaiting_refund_details'
            session['last_intent'] = 'refund'
            return self.ask_for_refund_details()
        
        elif 'product' in message_lower or 'catalog' in message_lower:
            session['state'] = 'awaiting_product_name'
            session['last_intent'] = 'product'
            return self.ask_for_product_name()
        
        elif 'discount' in message_lower or 'coupon' in message_lower or 'promo' in message_lower:
            return self.show_discounts(session)
        
        elif 'shipping' in message_lower or 'delivery' in message_lower:
            return self.show_shipping_info(session)
        
        elif 'human' in message_lower or 'agent' in message_lower or 'talk to' in message_lower:
            session['state'] = 'awaiting_ticket_details'
            session['last_intent'] = 'human_support'
            return self.ask_for_ticket_details()
        
        elif 'help' in message_lower or 'menu' in message_lower:
            return self.show_help(session)
        
        elif 'hello' in message_lower or 'hi' in message_lower or 'hey' in message_lower:
            return self.show_welcome(session)
        
        elif 'thanks' in message_lower or 'thank' in message_lower:
            return self.acknowledge_thanks(session)
        
        else:
            return self.handle_unknown(session)
    
    def ask_for_order_number(self):
        return """📦 **Order Tracking**

Please enter your order number to check status.

**Format:** ORD-12345

*Example: ORD-12345*

💡 You can find your order number in your confirmation email.

Enter order number:"""
    
    def handle_order_number_provided(self, message, session, user_id):
        order_match = re.search(r'ORD-\d{5}', message.upper())
        
        if order_match:
            order_num = order_match.group()
            if order_num in ORDER_DATABASE:
                order = ORDER_DATABASE[order_num]
                session['state'] = 'idle'
                
                response = f"""✅ **Order Found!**

━━━━━━━━━━━━━━━━━━
📦 **Order Number:** {order_num}
🛍️ **Product:** {order['product']}
💰 **Amount:** {order['total']}
📅 **Order Date:** {order['date']}
📊 **Status:** {order['status']}
"""
                if 'tracking' in order:
                    response += f"🔢 **Tracking:** {order['tracking']}\n"
                if 'expected_date' in order:
                    response += f"📅 **Expected Delivery:** {order['expected_date']}\n"
                if 'delivered_date' in order:
                    response += f"✅ **Delivered On:** {order['delivered_date']}\n"
                
                response += """
━━━━━━━━━━━━━━━━━━

**What would you like to do next?**
• Track another order
• Request refund
• Check shipping
• Talk to human

Just type your request!"""
                return response
            else:
                return f"""❌ **Order {order_num} not found.**

Please check:
• Order number is correct
• Try: ORD-12345, ORD-67890, or ORD-11111

Enter correct order number:"""
        else:
            return """❌ **Invalid order number format.**

Please use format: **ORD-12345**

Example: ORD-12345

Enter order number:"""
    
    def ask_for_refund_details(self):
        return """💰 **Refund Request**

Please provide the following details:

1. **Order number** (e.g., ORD-12345)
2. **Reason for refund** (e.g., defective, wrong item, damaged)

**Example:** ORD-12345, product arrived damaged

Enter refund details:"""
    
    def handle_refund_details_provided(self, message, session, user_id):
        order_match = re.search(r'ORD-\d{5}', message.upper())
        
        if order_match:
            order_num = order_match.group()
            if order_num in ORDER_DATABASE:
                ticket_id = self.create_ticket(user_id, 'Refund', message)
                session['state'] = 'idle'
                
                return f"""✅ **Refund Request Submitted!**

━━━━━━━━━━━━━━━━━━
🎫 **Ticket ID:** {ticket_id}
📦 **Order:** {order_num}
💰 **Refund Amount:** {ORDER_DATABASE[order_num]['total']}
⏱️ **Processing Time:** 24-48 hours
━━━━━━━━━━━━━━━━━━

**Next Steps:**
1. Our team will review your request
2. You'll receive email confirmation
3. Refund processed in 5-7 business days

**Need immediate help?** Call: +1 (800) 123-4567

Would you like to do anything else?"""
            else:
                return f"❌ Order {order_num} not found. Please check and try again.\n\nEnter valid order number:"
        else:
            return "❌ Please include your order number in format: ORD-12345\n\nExample: ORD-12345, product is defective"
    
    def ask_for_product_name(self):
        return """🛍️ **Product Information**

Which product would you like to know about?

**Available products:**
• Headphones ($49.99)
• Smart Watch ($129.99)
• Speaker ($79.99)

Type product name (e.g., "headphones"):"""
    
    def handle_product_query(self, message, session, user_id):
        message_lower = message.lower()
        
        for product_key, details in PRODUCTS.items():
            if product_key in message_lower:
                session['state'] = 'idle'
                return f"""🛍️ **{details['name']}**

💰 **Price:** {details['price']}
📦 **Availability:** {details['stock']}
⭐ **Rating:** 4.5/5 (Based on 1,200+ reviews)

**Key Features:**
• Premium quality
• 1-year warranty
• Free shipping

**Would you like to:**
• Check other products
• Apply discount
• Place order
• Ask about warranty

What would you like to do?"""
        
        session['state'] = 'idle'
        return """❌ Product not found.

**Available products:**
• Headphones ($49.99)
• Smart Watch ($129.99)
• Speaker ($79.99)

Type "Products" to see catalog again."""
    
    def ask_for_ticket_details(self):
        return """👤 **Human Support Request**

Please describe your issue briefly so I can connect you to the right agent.

**Example:** "My order hasn't arrived and it's been 10 days"

Describe your issue:"""
    
    def handle_ticket_creation(self, message, session, user_id):
        ticket_id = self.create_ticket(user_id, 'Human Support', message)
        session['state'] = 'idle'
        
        return f"""✅ **Support Ticket Created!**

━━━━━━━━━━━━━━━━━━
🎫 **Ticket ID:** {ticket_id}
👤 **Priority:** Normal
⏱️ **Response Time:** 2-4 hours
━━━━━━━━━━━━━━━━━━

**Our team will contact you via email.**

**Alternative contact:**
📞 Phone: +1 (800) 123-4567 (9AM-6PM EST)
📧 Email: support@example.com

Please keep your ticket ID for reference.

Anything else I can help with?"""
    
    def show_discounts(self, session):
        session['state'] = 'idle'
        return """🎉 **Active Discounts & Offers** 🎉

━━━━━━━━━━━━━━━━━━
🔥 **WELCOME10** → 10% off first order
🔥 **SAVE20** → 20% off orders $100+
🔥 **FREESHIP** → Free shipping on $50+
━━━━━━━━━━━━━━━━━━

**How to use:**
Enter code at checkout

**Valid until:** December 31, 2025

Would you like to know about our ongoing sale?"""
    
    def show_shipping_info(self, session):
        session['state'] = 'idle'
        return """🚚 **Shipping Information**

━━━━━━━━━━━━━━━━━━
**Domestic:**
• Standard: 3-5 days ($0)
• Express: 1-2 days ($9.99)
• Overnight: Next day ($19.99)

**International:**
• Standard: 7-14 days ($19.99)
• Express: 5-7 days ($39.99)

━━━━━━━━━━━━━━━━━━

**Free shipping on orders $50+!**

Would you like to track an order?"""
    
    def show_help(self, session):
        session['state'] = 'idle'
        return """📋 **Available Commands**

━━━━━━━━━━━━━━━━━━
**Orders & Shipping:**
• "Order status" - Track your order
• "Shipping" - Delivery info

**Money & Returns:**
• "Refund" - Request refund
• "Discount" - Show coupons

**Products & Support:**
• "Products" - View catalog
• "Human support" - Talk to agent
• "Help" - Show this menu

━━━━━━━━━━━━━━━━━━

**Example conversation:**
You: "Order status"
Bot: Asks for order number
You: "ORD-12345"
Bot: Shows order details

What would you like help with?"""
    
    def show_welcome(self, session):
        session['state'] = 'idle'
        return """👋 **Welcome to AI Customer Support!**

I'm here to help you 24/7. Here's what I can do:

━━━━━━━━━━━━━━━━━━
📦 **Track orders** - Check delivery status
💰 **Process refunds** - Get money back
🎟️ **Apply discounts** - Save money
🛍️ **Product info** - Learn about items
👤 **Human support** - Talk to an agent
━━━━━━━━━━━━━━━━━━

**Let's get started!** 

What would you like help with today?

💡 Try: "Order status" or "Help" """
    
    def acknowledge_thanks(self, session):
        session['state'] = 'idle'
        return """😊 **You're welcome!**

I'm glad I could help.

Is there anything else you need assistance with?

💡 Try: "Order status", "Discount", or "Help" """
    
    def handle_unknown(self, session):
        session['state'] = 'idle'
        return """🤔 **I didn't understand that.**

Let me help you better:

━━━━━━━━━━━━━━━━━━
**Try these commands:**
• "Order status" - Track order
• "Refund" - Request refund
• "Discount" - Show coupons
• "Products" - View catalog
• "Help" - All commands
━━━━━━━━━━━━━━━━━━

Type "Help" to see complete menu!"""
    
    def create_ticket(self, user_id, ticket_type, description):
        ticket_id = f"TKT-{str(uuid.uuid4())[:8].upper()}"
        tickets[ticket_id] = {
            'user_id': user_id,
            'type': ticket_type,
            'description': description,
            'status': 'Open',
            'created_at': datetime.now().isoformat()
        }
        return ticket_id

# Initialize bot
bot = ProductionBot()

# ============================================
# HTML TEMPLATE
# ============================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI Customer Support | Production Level</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .chat {
            width: 550px;
            height: 750px;
            background: white;
            border-radius: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }

        .header h1 { font-size: 22px; margin-bottom: 5px; }
        .status { font-size: 11px; opacity: 0.9; }
        .dot { display: inline-block; width: 8px; height: 8px; background: #4ade80; border-radius: 50%; animation: pulse 2s infinite; margin-right: 5px; }
        @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }

        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f5f7fb;
        }

        .msg {
            margin-bottom: 15px;
            display: flex;
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .msg-content {
            max-width: 75%;
            padding: 12px 16px;
            border-radius: 20px;
            font-size: 14px;
            line-height: 1.4;
            white-space: pre-wrap;
        }
        .user .msg-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .bot .msg-content {
            background: white;
            color: #333;
            border: 1px solid #ddd;
        }
        .time { font-size: 10px; color: #999; margin-top: 5px; margin-left: 10px; }

        .typing {
            display: none;
            padding: 12px 16px;
            background: white;
            border-radius: 20px;
            width: fit-content;
            margin-bottom: 15px;
        }
        .typing span {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #999;
            margin: 0 2px;
            animation: typingAnim 1.4s infinite;
        }
        @keyframes typingAnim {
            0%,60%,100% { transform: translateY(0); }
            30% { transform: translateY(-8px); }
        }
        .typing span:nth-child(2) { animation-delay: 0.2s; }
        .typing span:nth-child(3) { animation-delay: 0.4s; }

        .quick {
            padding: 10px 20px;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            background: #f5f7fb;
            border-top: 1px solid #ddd;
        }
        .quick-btn {
            background: white;
            border: 1px solid #ddd;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            cursor: pointer;
            transition: 0.2s;
        }
        .quick-btn:hover { background: #667eea; color: white; }

        .input-area {
            padding: 20px;
            background: white;
            border-top: 1px solid #ddd;
            display: flex;
            gap: 10px;
        }
        .input-area input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #ddd;
            border-radius: 25px;
            outline: none;
            font-size: 14px;
        }
        .input-area input:focus { border-color: #667eea; }
        .input-area button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="chat">
        <div class="header">
            <h1>🤖 AI Customer Support</h1>
            <div class="status"><span class="dot"></span> Online 24/7 • Production Level</div>
        </div>
        
        <div class="messages" id="messages">
            <div class="msg bot">
                <div class="msg-content">
                    👋 Welcome! I'm your AI support agent.<br><br>
                    <strong>I can help you step by step:</strong><br>
                    • 📦 Track orders<br>
                    • 💰 Process refunds<br>
                    • 🎟️ Apply discounts<br>
                    • 🛍️ Product info<br><br>
                    <strong>Try:</strong> "Order status" → I'll ask for order number → You provide it → I show details<br><br>
                    Type "Help" to see all commands!
                </div>
            </div>
        </div>
        
        <div class="typing" id="typing"><span></span><span></span><span></span></div>
        
        <div class="quick">
            <div class="quick-btn" onclick="sendMsg('Order status')">📦 Order Status</div>
            <div class="quick-btn" onclick="sendMsg('Refund')">💰 Refund</div>
            <div class="quick-btn" onclick="sendMsg('Discount')">🎟️ Discount</div>
            <div class="quick-btn" onclick="sendMsg('Products')">🛍️ Products</div>
            <div class="quick-btn" onclick="sendMsg('Human support')">👤 Human</div>
            <div class="quick-btn" onclick="sendMsg('Help')">📋 Help</div>
        </div>
        
        <div class="input-area">
            <input type="text" id="input" placeholder="Type your message..." onkeypress="handleEnter(event)">
            <button onclick="sendMsg()">Send →</button>
        </div>
    </div>

    <script>
        async function sendMsg(msg) {
            const input = document.getElementById('input');
            const message = msg || input.value.trim();
            if (!message) return;
            
            addMessage(message, 'user');
            if (!msg) input.value = '';
            
            document.getElementById('typing').style.display = 'block';
            scrollToBottom();
            
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                });
                const data = await res.json();
                document.getElementById('typing').style.display = 'none';
                addMessage(data.reply, 'bot');
            } catch(e) {
                document.getElementById('typing').style.display = 'none';
                addMessage('Connection error. Please refresh.', 'bot');
            }
        }
        
        function addMessage(text, sender) {
            const div = document.createElement('div');
            div.className = `msg ${sender}`;
            const time = new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
            div.innerHTML = `<div class="msg-content">${text.replace(/\\n/g, '<br>')}</div><div class="time">${time}</div>`;
            document.getElementById('messages').appendChild(div);
            scrollToBottom();
        }
        
        function scrollToBottom() {
            const msgs = document.getElementById('messages');
            msgs.scrollTop = msgs.scrollHeight;
        }
        
        function handleEnter(e) {
            if (e.key === 'Enter') sendMsg();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    user_id = request.remote_addr
    reply = bot.process_message(message, user_id)
    return jsonify({'reply': reply})

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   🤖 PRODUCTION LEVEL AI CUSTOMER SUPPORT               ║
    ║                                                          ║
    ║   ✅ Server Running: http://localhost:5000              ║
    ║                                                          ║
    ║   🔥 KEY FEATURES:                                      ║
    ║      • Conversation Memory (remembers context)          ║
    ║      • Step-by-Step Flow                                ║
    ║      • State Management                                 ║
    ║      • One-by-One Questioning                          ║
    ║                                                          ║
    ║   📝 TEST FLOW:                                         ║
    ║      1. Type "Order status"                            ║
    ║      2. Bot asks for order number                      ║
    ║      3. Type "ORD-12345"                               ║
    ║      4. Bot shows order details                        ║
    ║                                                          ║
    ║   Press CTRL+C to stop                                  ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    app.run(debug=True, host='0.0.0.0', port=5000)
