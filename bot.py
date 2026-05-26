import os
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Caption templates for different platforms
CAPTIONS = {
    'instagram': {
        'funny': [
            "😂 Living my best life, one post at a time! #NoRegrets",
            "My life isn't perfect, but my captions are 🔥",
            "Warning: May contain excessive happiness 🚀",
            "I'm not lazy, I'm in energy-saving mode 💤"
        ],
        'inspiring': [
            "✨ Dream big. Work hard. Stay humble.",
            "Your only limit is your mind. Break free! 💪",
            "Small steps every day lead to big results 🌟",
            "Believe in yourself and anything is possible 🚀"
        ],
        'business': [
            "Building empires, one decision at a time 💼",
            "Success is not given, it's earned. Let's grind! 📈",
            "Your brand is what people say about you when you leave the room",
            "Invest in yourself. It's the best ROI you'll ever get 💰"
        ],
        'love': [
            "💕 You, me, and endless cups of coffee",
            "Every love story is beautiful, but ours is my favorite 💑",
            "Home is wherever I'm with you 🏠❤️",
            "Falling for you more every single day 💘"
        ],
        'travel': [
            "✈️ Wander often, wonder always",
            "Collecting memories, not things 🌍",
            "Adventure is out there! Go find it 🗺️",
            "Passport full of stamps, heart full of joy 📸"
        ]
    },
    'facebook': {
        'funny': [
            "🤣 That moment when you realize it's Monday again...",
            "My superpower? Finding things I just lost. 5 minutes later.",
            "Adulting: 0/10, would not recommend 🥲",
            "I followed my heart, it led me to the fridge 🍕"
        ],
        'inspiring': [
            "🌅 Every sunrise is a new opportunity. Make it count!",
            "Don't watch the clock. Do what it does. Keep going.",
            "Your vibe attracts your tribe. Stay positive! ✨",
            "The best project you'll ever work on is YOU"
        ],
        'business': [
            "💼 Success doesn't come from comfort zones.",
            "Your network is your net worth. Build it wisely!",
            "Stop waiting for the 'perfect time'. Create it! 🎯",
            "Consistency > Intensity. Show up every day!"
        ],
        'love': [
            "❤️ Grateful for the little moments that mean everything",
            "Love is when two people know everything about each other and are still friends",
            "You make my world brighter just by being in it 🌟"
        ],
        'travel': [
            "🌎 Not all who wander are lost. Some are just finding themselves.",
            "Take only pictures, leave only footprints 🦶",
            "Life is short, book the trip! ✈️",
            "Adventure may hurt you but monotony will kill you"
        ]
    },
    'twitter': {
        'funny': [
            "My therapist said I need to stop living in the past... so I deleted my old tweets 🐦",
            "I put the 'pro' in procrastination 😅",
            "Running on caffeine and chaos ☕",
            "My sleep schedule is a suggestion, not a rule"
        ],
        'inspiring': [
            "💫 Start where you are. Use what you have. Do what you can.",
            "The comeback is always stronger than the setback",
            "Your story isn't over yet. Keep writing 📖"
        ],
        'business': [
            "📊 Data > Opinions. Let the numbers speak.",
            "Build your brand like your life depends on it. Because it does.",
            "Stop scrolling. Start doing. 🎯"
        ],
        'love': [
            "💝 Love is friendship set on fire",
            "You + Me = Infinite possibilities",
            "Every love song makes sense now 🎵"
        ],
        'travel': [
            "📍 Current location: Somewhere amazing",
            "Wanderlust and city dust 🏙️",
            "Living that jet-set life ✈️"
        ]
    },
    'linkedin': {
        'business': [
            "💡 3 lessons I learned from failure: \n1. It's temporary \n2. It's a teacher \n3. It's necessary",
            "Your career is a marathon, not a sprint. Pace yourself 🏃‍♂️",
            "The best time to plant a tree was 20 years ago. The second best time is NOW 🌳",
            "Leadership is not about being in charge. It's about taking care of those in your charge"
        ],
        'inspiring': [
            "🚀 Don't be afraid to start over. It's a chance to build something better.",
            "Your network is your superpower. Use it wisely!",
            "Growth happens when you're uncomfortable. Embrace the grind 📈"
        ]
    },
    'tiktok': {
        'funny': [
            "POV: You're supposed to be productive but here we are 🤡",
            "This audio has me in a chokehold 🎵",
            "My toxic trait is thinking I can dance 💃",
            "Wait for it... (nothing happens) 🙃"
        ],
        'trending': [
            "✨ The glow up is real ✨",
            "And they said it couldn't be done...",
            "Tag someone who needs to see this 👇",
            "This is your sign to go for it 🚦"
        ]
    }
}

# Store user preferences
user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("📸 Instagram", callback_data='platform_instagram')],
        [InlineKeyboardButton("📘 Facebook", callback_data='platform_facebook')],
        [InlineKeyboardButton("🐦 Twitter/X", callback_data='platform_twitter')],
        [InlineKeyboardButton("💼 LinkedIn", callback_data='platform_linkedin')],
        [InlineKeyboardButton("🎵 TikTok", callback_data='platform_tiktok')],
        [InlineKeyboardButton("❓ How to use", callback_data='how_to_use')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✍️ **Welcome to CaptionCrafteerBot, {user.first_name}!**\n\n"
        f"I generate creative captions for all your social media needs.\n\n"
        f"**Choose a platform to get started:**",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith('platform_'):
        platform = data.split('_')[1]
        user_sessions[query.from_user.id] = {'platform': platform}
        
        # Show mood options for selected platform
        moods = ['funny', 'inspiring', 'business', 'love', 'travel']
        available_moods = [m for m in moods if m in CAPTIONS.get(platform, {})]
        
        keyboard = [[InlineKeyboardButton(mood.capitalize(), callback_data=f'mood_{mood}')] for mood in available_moods]
        keyboard.append([InlineKeyboardButton("🔙 Back to Platforms", callback_data='back_to_platforms')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🎨 **{platform.upper()}** selected!\n\n"
            f"Now choose the vibe for your caption:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif data.startswith('mood_'):
        mood = data.split('_')[1]
        user_id = query.from_user.id
        
        if user_id not in user_sessions:
            await query.edit_message_text("Please start over with /start")
            return
        
        platform = user_sessions[user_id]['platform']
        
        # Get random caption
        if platform in CAPTIONS and mood in CAPTIONS[platform]:
            captions_list = CAPTIONS[platform][mood]
            caption = random.choice(captions_list)
            
            # Add hashtags for Instagram
            if platform == 'instagram':
                caption += f"\n\n#SocialMedia #ContentCreator #{platform.capitalize()}"
            
            keyboard = [
                [InlineKeyboardButton("🔄 Generate Another", callback_data=f'mood_{mood}')],
                [InlineKeyboardButton("📱 New Platform", callback_data='back_to_platforms')],
                [InlineKeyboardButton("📋 Copy Caption", callback_data=f'copy_{caption[:50]}')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"**✨ Your {platform.upper()} {mood} Caption:**\n\n"
                f"_{caption}_\n\n"
                f"What would you like to do next?",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    elif data == 'back_to_platforms':
        keyboard = [
            [InlineKeyboardButton("📸 Instagram", callback_data='platform_instagram')],
            [InlineKeyboardButton("📘 Facebook", callback_data='platform_facebook')],
            [InlineKeyboardButton("🐦 Twitter/X", callback_data='platform_twitter')],
            [InlineKeyboardButton("💼 LinkedIn", callback_data='platform_linkedin')],
            [InlineKeyboardButton("🎵 TikTok", callback_data='platform_tiktok')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "**Choose a platform:**",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif data == 'how_to_use':
        await query.edit_message_text(
            "**📖 How to use CaptionCrafteerBot:**\n\n"
            "1️⃣ Select your social media platform\n"
            "2️⃣ Choose the mood/vibe you want\n"
            "3️⃣ Get a ready-to-use caption!\n"
            "4️⃣ Generate unlimited variations\n\n"
            "**Available moods:**\n"
            "• Funny 😂\n"
            "• Inspiring ✨\n"
            "• Business 💼\n"
            "• Love ❤️\n"
            "• Travel ✈️\n\n"
            "Click /start to begin!",
            parse_mode='Markdown'
        )
    
    elif data.startswith('copy_'):
        await query.answer("📋 Caption copied! (In Telegram web/desktop, you can select and copy)")

async def custom_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle custom caption requests"""
    user_message = update.message.text
    
    if len(user_message.split()) > 5:
        # User provided topic/description
        await update.message.reply_text(
            f"✍️ Generating caption for: *{user_message[:50]}...*\n\n"
            f"**Here's a sample caption:**\n\n"
            f"✨ {user_message[:100]} ✨\n\n"
            f"🔥 Like this? Use the buttons above to get more variations!\n"
            f"Or send /start to choose a platform.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "Send me a topic or description, and I'll create a caption for you!\n\n"
            "Example: 'My morning coffee routine' ☕\n\n"
            "Or use /start for platform-specific captions"
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "**CaptionCrafteerBot Commands:**\n\n"
        "/start - Start the bot\n"
        "/help - Show this help\n"
        "/random - Get a random caption\n"
        "/platforms - Show all platforms\n\n"
        "Or just send me any topic and I'll create a caption!",
        parse_mode='Markdown'
    )

async def random_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate completely random caption"""
    all_platforms = list(CAPTIONS.keys())
    random_platform = random.choice(all_platforms)
    all_moods = list(CAPTIONS[random_platform].keys())
    random_mood = random.choice(all_moods)
    caption = random.choice(CAPTIONS[random_platform][random_mood])
    
    await update.message.reply_text(
        f"🎲 **Random Caption** ({random_platform.upper()} - {random_mood}):\n\n"
        f"_{caption}_\n\n"
        f"Want more? Use /start to customize!",
        parse_mode='Markdown'
    )

async def platforms_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    platforms_list = "\n".join([f"• {p.upper()}" for p in CAPTIONS.keys()])
    await update.message.reply_text(
        f"**Supported Platforms:**\n\n{platforms_list}\n\n"
        f"Use /start to get captions for any platform!",
        parse_mode='Markdown'
    )

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not set!")
        return
    
    app = Application.builder().token(token).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("random", random_caption))
    app.add_handler(CommandHandler("platforms", platforms_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, custom_caption))
    
    print("✍️ CaptionCrafteerBot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
