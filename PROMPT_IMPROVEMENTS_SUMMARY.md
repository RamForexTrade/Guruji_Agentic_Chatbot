# Conversation Prompt Improvements - Natural & Caring Responses

## Problem Identified

The chatbot was using **repetitive, stereotypical therapy-speak** patterns:
- ❌ "I hear you, Ashwini, and..."
- ❌ "I hear you, [name], and it sounds like..."
- ❌ Starting every response the same way
- ❌ Sounding like a therapist/counselor instead of a caring friend

This made conversations feel **scripted, robotic, and unnatural** rather than genuine and caring.

---

## Root Cause

The system prompt had:
1. **Weak prohibition** on formulaic phrases (just "Avoid..." instead of strong bans)
2. **Limited examples** of varied conversation starters
3. **Formulaic patterns** in the examples themselves
4. Not enough emphasis on **variety and spontaneity**
5. The 120B parameter model is powerful enough to follow patterns - but it was learning the WRONG patterns

---

## Solutions Implemented

### 1. **Stronger Prohibitions** (v3_system_prompts.yaml)

**Before:**
```yaml
Avoid "I hear you" or "I appreciate your honesty."
```

**After:**
```yaml
**ABSOLUTELY FORBIDDEN - DO NOT USE THESE PHRASES EVER:**
❌ "I hear you"
❌ "I hear you, [name], and..."
❌ "I appreciate you sharing"
❌ "Thank you for opening up"
❌ "It sounds like..."
❌ "What I'm hearing is..."
❌ Any repetitive therapy-speak patterns
```

### 2. **Natural Conversation Guidelines**

Added explicit instructions on how to sound natural:
```yaml
**HOW TO RESPOND NATURALLY:**
✅ Start differently every single time
✅ Vary your opening words - don't follow a template
✅ Sound like texting a friend, not a counselor
✅ Use natural reactions: "Yeah,", "Hmm,", "That's rough,", "Oof,", "Right,", etc.
✅ Mirror their energy and words
✅ Keep it SHORT - 2-3 sentences maximum
✅ Jump straight to the point - no filler
```

### 3. **Varied Examples for Each Stage**

**EMOTION Stage - Before:**
```
- "That sounds tough..."
- "Hmm, I can sense that's been weighing on you..."
- "Yeah, that can be heavy..."
```

**EMOTION Stage - After:**
```
Examples of VARIED openings (pick different styles, NEVER repeat patterns):
- "That's rough. What's been making you feel this way?"
- "Yeah, totally get that. What's going on?"
- "Hmm. What's been weighing on you?"
- "Oof, that's heavy. Want to share what's happening?"
- "Right, when things feel off like that... what's been bothering you most?"
- "That sounds really hard. What's been going on lately?"
- "Makes sense you'd feel lost. What's making you feel stuck?"
```

### 4. **Updated Core Principles**

**Before:**
```
- Vary tone – Never sound like reading from a template
- Avoid "therapist voice" – Stay grounded and conversational
```

**After:**
```
- START EACH RESPONSE DIFFERENTLY - never use the same opening pattern twice
- ABSOLUTELY FORBIDDEN: "I hear you", "I hear you [name]", "I appreciate...", etc.
- Instead use natural reactions: "Yeah,", "Hmm,", "That's rough,", "Oof,", "Right,", "Makes sense,"
- Sound like texting a caring friend, NOT like a professional giving therapy
- MAXIMUM VARIETY – Every response must start differently. Track your patterns and break them
- NO "therapist voice" – Absolutely forbidden. You're a friend texting, not a counselor in session
- Spontaneous, not scripted – Sound alive and in-the-moment, not following a template
```

### 5. **Shortened Response Length**

**Before:** 3-4 sentences max
**After:** 2-3 sentences MAXIMUM

This prevents long-winded responses and keeps conversations snappy and natural.

### 6. **Updated Age-Specific Examples**

Made examples more casual and varied:
```
| 18–25 | "Oof, that's rough. What's been bothering you most?" /
         "Yeah, when life feels messy like that... what's going on?" |
| 26–35 | "That sounds heavy. What's been happening?" /
         "Right, makes sense you'd feel that way. What's going on?" |
| 36–45 | "That's a lot to carry. What's been weighing on you?" /
         "Yeah, I can see why that'd feel heavy. What's happening?" |
```

---

## Expected Results

After these changes, conversations should feel:

✅ **Natural** - Like texting a caring friend
✅ **Varied** - Different opening every time
✅ **Spontaneous** - Alive and in-the-moment
✅ **Genuine** - Real empathy, not scripted
✅ **Concise** - Short, focused responses
✅ **Caring** - Warm without being clinical
✅ **Reflective** - Sometimes echoes back what user said to show listening
✅ **Humanized** - Uses natural acknowledgments like "Thanks for sharing", "No worries", etc.

### Example Conversation Flow (Updated Style with Echo & Natural Reactions):

**User:** "I don't know what is happening with me?"

**Bot:** "Thanks for sharing. So you're not sure what's happening... what emotions are coming up?"

**User:** "nothing working out, I feel I am lost"

**Bot:** "Got it. Nothing working out can feel overwhelming. Is this work, relationships, or everything?"

**User:** "My boss is not giving importance to me"

**Bot:** "Your boss not giving you importance... that's frustrating. Are you at work now or home?"

---

### Key Improvements (V2 - Latest):

1. **Echo technique** - Sometimes reflects back their words: "So you're not sure what's happening...", "Your boss not giving you importance..."
2. **Expanded natural reactions** - Now includes:
   - "Thanks for sharing", "Thanks for opening up", "Appreciate that"
   - "No worries", "I get it", "Got it", "Okay"
   - Original variety: "Yeah,", "Hmm,", "That's rough,", "Oof,", "Right,"
3. **More humanized** - Feels like a real person showing they're listening
4. **Different every time** - Still never repeats the same opening pattern

---

## Files Modified

1. **system_prompts.yaml** (THE CORRECT FILE - this is what the code actually uses!)
   - Lines 32-39: Updated Conversational Philosophy
   - Lines 41-46: Updated Emotional Style Guide with varied examples
   - Lines 48-56: Strengthened Core Principles
   - Lines 66-188: Complete rewrite of conversation_prompt section with strong prohibitions

**Note:** The code loads prompts from `system_prompts.yaml` as configured in `utils/config_loader.py` line 21.
`v3_system_prompts.yaml` was also updated for consistency, but it's not currently being used by the application.

---

## Testing Recommendations

1. **Test with various emotional states:**
   - Anxiety, confusion, sadness, stress
   - Verify each response starts differently

2. **Test multiple conversation turns:**
   - Ensure NO repetition of opening patterns
   - Check for natural, varied language

3. **Test age ranges:**
   - 18-25: Should be casual and modern
   - 26-35: Should be grounded and relatable
   - 36-45: Should be calm and wise

4. **Verify response length:**
   - Should be 2-3 sentences max
   - Should feel like texting, not essay writing

---

## Model Used

**Model:** `openai/gpt-oss-120b` (120B parameters via Groq)
**Temperature:** 0.7 (as configured in config.yaml)

The 120B model is powerful enough to follow nuanced instructions and generate varied, natural responses - we just needed to give it the right guidance!

---

## Next Steps

1. **Restart the chatbot** to load the new prompts
2. **Test conversations** and verify natural variety
3. **Monitor for any new patterns** that emerge
4. **Fine-tune** if needed based on real conversations

---

## Notes

- The changes maintain all existing functionality (assessment stages, information gathering)
- Only the **conversation style** has been improved - the **logic** remains the same
- If you notice any new repetitive patterns, we can add them to the FORBIDDEN list
- The prompt now explicitly instructs the model to **track its patterns and break them**

---

**JAI GURU DEV** 🙏

*Last Updated: November 2025*
