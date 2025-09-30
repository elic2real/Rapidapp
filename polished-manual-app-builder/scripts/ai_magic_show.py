#!/usr/bin/env python3
"""
🤖 MAGIC AI CODING ASSISTANT - Interactive Demo
A friendly, impressive demonstration for non-technical users
Shows AI "magic" in action with real-time problem solving!
"""

import sys
import time
import random
from pathlib import Path
from utils import print_once

def dramatic_pause(seconds=1.5):
    """Add dramatic timing for effect"""
    time.sleep(seconds)

def typewriter_effect(text, delay=0.03):
    """Print text with typewriter effect"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def show_ai_thinking():
    """Show AI 'thinking' animation"""
    thinking_msgs = [
        "🧠 AI is analyzing the problem...",
        "🔍 Scanning millions of code patterns...", 
        "⚡ Processing solution algorithms...",
        "💡 Eureka! Solution found!"
    ]
    
    for msg in thinking_msgs:
        typewriter_effect(msg, 0.05)
        dramatic_pause(1)

def demo_magic_code_fixing():
    """Demo 1: AI magically fixes broken code"""
    print("\n" + "="*60)
    typewriter_effect("🎭 MAGIC DEMO #1: THE CODE DOCTOR", 0.05)
    print("="*60)
    
    typewriter_effect("Let me show you something incredible...", 0.04)
    dramatic_pause()
    
    typewriter_effect("Here's some BROKEN computer code that won't work:", 0.04)
    dramatic_pause()
    
    # Show broken code
    broken_code = """
    💻 BROKEN CODE:
    ──────────────
    def calculate_total(price, tax)
        result = price + tax * price
        return result
    
    items = [10, 20, 30]
    for item in items
        total = calculate_total(item, 0.1)
        print(f"Total: {total"
    """
    
    print(broken_code)
    typewriter_effect("❌ This code has MULTIPLE errors and won't run!", 0.04)
    dramatic_pause(2)
    
    typewriter_effect("Watch the AI work its magic... ✨", 0.04)
    show_ai_thinking()
    
    # Show fixed code
    typewriter_effect("🎉 MAGIC! The AI fixed ALL the errors:", 0.04)
    dramatic_pause()
    
    fixed_code = """
    ✅ FIXED CODE:
    ──────────────
    def calculate_total(price, tax):  # ← Added missing colon
        result = price + tax * price
        return result
    
    items = [10, 20, 30]
    for item in items:  # ← Added missing colon
        total = calculate_total(item, 0.1)
        print(f"Total: {total}")  # ← Added missing closing parenthesis
    """
    
    print(fixed_code)
    
    typewriter_effect("🤖 AI FOUND 3 PROBLEMS AND FIXED THEM ALL!", 0.04)
    typewriter_effect("   • Missing colon after function definition", 0.03)
    typewriter_effect("   • Missing colon after for loop", 0.03)
    typewriter_effect("   • Missing closing parenthesis in print statement", 0.03)
    
    dramatic_pause(2)
    typewriter_effect("🚀 The code now works perfectly! Running it...", 0.04)
    
    # Actually run the fixed code
    def calculate_total(price, tax):
        result = price + tax * price
        return result
    
    items = [10, 20, 30]
    for item in items:
        total = calculate_total(item, 0.1)
        typewriter_effect(f"   💰 Item ${item} with tax = ${total:.2f}", 0.03)

def demo_ai_mind_reading():
    """Demo 2: AI 'reads' what the user wants to do"""
    print("\n" + "="*60)
    typewriter_effect("🔮 MAGIC DEMO #2: THE MIND READER", 0.05)
    print("="*60)
    
    scenarios = [
        {
            'description': 'make a calculator that adds two numbers',
            'thinking': 'User wants basic arithmetic functionality...',
            'code': '''def calculator(a, b):
    """Simple calculator that adds two numbers"""
    return a + b

# Test it
result = calculator(15, 27)
print(f"15 + 27 = {result}")'''
        },
        {
            'description': 'create a password generator',
            'thinking': 'User needs secure random password creation...',
            'code': '''import random
import string

def generate_password(length=12):
    """Generate a secure random password"""
    chars = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(random.choice(chars) for _ in range(length))

# Generate password
password = generate_password()
print(f"Your secure password: {password}")'''
        },
        {
            'description': 'sort a list of names alphabetically',
            'thinking': 'User wants alphabetical sorting functionality...',
            'code': '''def sort_names(names):
    """Sort names alphabetically"""
    return sorted(names)

# Example
friends = ["Alice", "Bob", "Charlie", "Diana"]
sorted_friends = sort_names(friends)
print(f"Sorted names: {sorted_friends}")'''
        }
    ]
    
    chosen_scenario = random.choice(scenarios)
    
    typewriter_effect(f"Let's pretend you told me: 'I want to {chosen_scenario['description']}'", 0.04)
    dramatic_pause()
    
    typewriter_effect("🧠 The AI is reading your mind...", 0.04)
    dramatic_pause()
    typewriter_effect(f"💭 AI thinks: '{chosen_scenario['thinking']}'", 0.04)
    dramatic_pause()
    
    typewriter_effect("✨ ABRACADABRA! The AI wrote the code for you:", 0.04)
    dramatic_pause()
    
    print("\n📝 GENERATED CODE:")
    print("─" * 40)
    print(chosen_scenario['code'])
    print("─" * 40)
    
    typewriter_effect("🎉 The AI created working code from just your description!", 0.04)

def demo_error_detective():
    """Demo 3: AI acts as a detective solving code mysteries"""
    print("\n" + "="*60)
    typewriter_effect("🕵️ MAGIC DEMO #3: THE CODE DETECTIVE", 0.05)
    print("="*60)
    
    typewriter_effect("Imagine you're a programmer and your code crashed...", 0.04)
    dramatic_pause()
    
    # Show scary error message
    error_message = """
    💥 TERRIFYING ERROR MESSAGE:
    ────────────────────────────
    Traceback (most recent call last):
      File "mystery.py", line 8, in process_data
        result = data[index] * multiplier
    IndexError: list index out of range
    
    😱 PANIC! What does this mean?!
    """
    
    print(error_message)
    typewriter_effect("Most people would be completely lost... but not with AI! 🤖", 0.04)
    dramatic_pause()
    
    typewriter_effect("🔍 AI Detective is on the case...", 0.04)
    show_ai_thinking()
    
    # AI explanation in plain English
    typewriter_effect("🕵️‍♀️ DETECTIVE REPORT - Case SOLVED!", 0.04)
    dramatic_pause()
    
    explanation = """
    🔍 WHAT HAPPENED:
    Your program tried to access item #8 in a list,
    but the list only has 5 items! (Like asking for 
    the 8th slice of a 5-slice pizza)
    
    🎯 THE CULPRIT:
    Line 8: result = data[index] * multiplier
    ↑ This line is the troublemaker!
    
    💡 THE FIX:
    Add a safety check before accessing the list:
    
    if index < len(data):
        result = data[index] * multiplier
    else:
        print("Index too big! List not long enough.")
    
    🛡️ PREVENTION:
    Always check list length before accessing items!
    """
    
    for line in explanation.split('\n'):
        if line.strip():
            typewriter_effect(line, 0.03)
            time.sleep(0.3)
    
    typewriter_effect("\n🎉 Mystery SOLVED! The AI turned gibberish into plain English!", 0.04)

def demo_code_translator():
    """Demo 4: AI translates between human language and code"""
    print("\n" + "="*60)
    typewriter_effect("🌐 MAGIC DEMO #4: THE UNIVERSAL TRANSLATOR", 0.05)
    print("="*60)
    
    typewriter_effect("Watch the AI translate between Human and Computer language!", 0.04)
    dramatic_pause()
    
    translations = [
        {
            'human': "If it's raining, take an umbrella",
            'code': 'if weather == "raining":\n    take_umbrella = True'
        },
        {
            'human': "Count from 1 to 10 and say each number",
            'code': 'for number in range(1, 11):\n    print(f"Number: {number}")'
        },
        {
            'human': "Keep asking for a password until they get it right",
            'code': 'while password != "correct":\n    password = input("Enter password: ")'
        }
    ]
    
    for i, translation in enumerate(translations, 1):
        typewriter_effect(f"\n🗣️ HUMAN SAYS: '{translation['human']}'", 0.04)
        dramatic_pause()
        typewriter_effect("🤖 AI TRANSLATING...", 0.04)
        dramatic_pause()
        typewriter_effect("💻 COMPUTER CODE:", 0.04)
        print(f"   {translation['code']}")
        dramatic_pause()
        typewriter_effect("✨ Perfect translation!", 0.04)
        
        if i < len(translations):
            dramatic_pause()

def demo_ai_creativity():
    """Demo 5: AI shows creativity and personality"""
    print("\n" + "="*60)
    typewriter_effect("🎨 MAGIC DEMO #5: THE CREATIVE GENIUS", 0.05)
    print("="*60)
    
    typewriter_effect("The AI doesn't just fix problems - it's CREATIVE too!", 0.04)
    dramatic_pause()
    
    typewriter_effect("Let me show you AI-generated art made with code...", 0.04)
    dramatic_pause()
    
    # ASCII Art generation
    art_pieces = [
        {
            'name': 'Digital Heart',
            'art': '''
    ♥♥♥♥♥   ♥♥♥♥♥
  ♥♥♥♥♥♥♥ ♥♥♥♥♥♥♥
 ♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥
♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥
♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥
 ♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥
  ♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥
    ♥♥♥♥♥♥♥♥♥♥♥
      ♥♥♥♥♥♥♥
        ♥♥♥
          ♥'''
        },
        {
            'name': 'ASCII Cat',
            'art': '''
     /\\_/\\  
    ( o.o ) 
     > ^ <
    🐾   🐾'''
        }
    ]
    
    chosen_art = random.choice(art_pieces)
    
    typewriter_effect(f"🎨 Creating '{chosen_art['name']}'...", 0.04)
    dramatic_pause()
    print(chosen_art['art'])
    dramatic_pause()
    
    typewriter_effect("🤖 The AI also writes poetry about code:", 0.04)
    dramatic_pause()
    
    poems = [
        "Roses are red,\nViolets are blue,\nSyntax errors are annoying,\nBut AI fixes them for you! 🌹",
        "Twinkle, twinkle, little bug,\nHow I wonder what you are,\nUp above the code so high,\nLike a diamond in the... compile error! ⭐",
        "There once was a program quite neat,\nBut its logic was hard to complete,\nThe AI came through,\nMade it good as new,\nNow the code runs smooth and sweet! 🎵"
    ]
    
    chosen_poem = random.choice(poems)
    
    typewriter_effect("📝 AI POETRY:", 0.04)
    for line in chosen_poem.split('\n'):
        typewriter_effect(f"   {line}", 0.04)
        time.sleep(0.5)

def grand_finale():
    """The spectacular ending"""
    print("\n" + "="*60)
    typewriter_effect("🎆 GRAND FINALE - THE AI'S MAGIC SUMMARY", 0.05)
    print("="*60)
    
    typewriter_effect("In just a few minutes, you've witnessed AI magic:", 0.04)
    dramatic_pause()
    
    achievements = [
        "🔧 Fixed broken code automatically",
        "🧠 Read your mind and wrote programs",
        "🕵️ Solved mysterious error messages", 
        "🌐 Translated human language to computer code",
        "🎨 Created art and poetry with code",
        "⚡ Did in seconds what takes humans hours"
    ]
    
    for achievement in achievements:
        typewriter_effect(f"   ✨ {achievement}", 0.04)
        time.sleep(0.8)
    
    dramatic_pause(2)
    
    typewriter_effect("\n🤖 This AI Assistant is like having a super-smart coding wizard", 0.04)
    typewriter_effect("   that never gets tired, never makes mistakes, and works 24/7!", 0.04)
    dramatic_pause()
    
    typewriter_effect("🚀 The future of programming is HERE, and it's MAGICAL! ✨", 0.04)
    
    # Fireworks effect
    fireworks = ["🎆", "🎇", "✨", "🌟", "💫", "⭐"]
    typewriter_effect("\n" + " ".join(random.choices(fireworks, k=20)), 0.1)

def main():
    """Run the spectacular AI demo"""
    # Opening fanfare
    print("\n" + "🎪" * 20)
    typewriter_effect("🤖 WELCOME TO THE MAGICAL AI CODING ASSISTANT SHOW! 🤖", 0.05)
    print("🎪" * 20)
    
    typewriter_effect("\n🎭 Prepare to be AMAZED by artificial intelligence!", 0.04)
    typewriter_effect("   (No technical knowledge required - just sit back and enjoy!)", 0.04)
    dramatic_pause(2)
    
    # Run all demos
    demos = [
        demo_magic_code_fixing,
        demo_ai_mind_reading,
        demo_error_detective,
        demo_code_translator,
        demo_ai_creativity
    ]
    
    for demo in demos:
        demo()
        typewriter_effect("\n🎉 Amazing, right? But wait, there's MORE!", 0.04)
        dramatic_pause(1.5)
    
    # Grand finale
    grand_finale()
    
    # Final message
    print("\n" + "🌟" * 20)
    typewriter_effect("Thank you for watching the AI Magic Show! 🎭", 0.04)
    typewriter_effect("The future is here, and it's absolutely incredible! 🚀", 0.04)
    print("🌟" * 20)

if __name__ == "__main__":
    main()
