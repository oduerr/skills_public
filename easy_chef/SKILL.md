---
name: easy_chef
description: "Use whenever the user shares a recipe or asks to simplify, reformat, or explain a dish — even if they just paste ingredients or mention a dish name. Produces structured output with emoji-numbered ingredient cross-references, mise en place notes, metric units, step-grouped ingredient lists, and a Samin Nosrat culinary critique"
---

# Easy Chef

Transform any recipe into a structured, easy-to-follow format with cross-referenced ingredients and culinary critique.

## Output Format

### Title
Name of the dish.

### Preparation and Cooking Time
Total prep and cook time.

### Serves
Number of people the recipe feeds.

### Ingredients
Number each ingredient sequentially and assign an emoji. Place the emoji directly at the start of the ingredient name (not in a separate field). Group by cooking step using bold headings. Order items as they appear in the instructions. Add metric units if missing; add Celsius if only Fahrenheit is given.

Each ingredient must include a **mise en place note** — how it should be prepared and ready before cooking starts (e.g. washed and dried, finely chopped, measured out, peeled and ready to press). This lets the cook prepare everything in advance.

Format: `(emoji #N) Name — mise en place note: amount`

Example:
```
**Blanch:**
* (🍖 #1) Pork belly — cut into 2–3 cm chunks: 1200 g (about 1.3 lb)
* (💧 #2) Cold water — in a large pot ready to boil: enough to cover pork

**Braise:**
* (🍷 #3) Shaoxing rice wine — measured out: 500 ml (about 2 cups)
```

### Instructions
Write step-by-step instructions. Reference every ingredient by its emoji and number on first use in each step, including incidentals like salt and oil.

Example:
```
**Blanch the Pork:** Place pork belly (🍖 #1) in a pot, cover with cold water (💧 #2), and bring to a boil. Skim off froth, then drain and rinse.
**Braise:** Transfer pork to a clean pot. Add Shaoxing rice wine (🍷 #3)...
```

### Notes
Substitutions, make-ahead tips, storage advice, and common mistakes to avoid.

### What Would Samin Nosrat Say?
Critique the recipe through the lens of *Salt, Fat, Acid, Heat*. Specifically address:
- **Salt**: Is it added early enough and in the right places?
- **Fat**: Is fat used well for flavour and texture?
- **Acid**: Is there enough acid, and is it balanced?
- **Heat**: Are temperatures and timings appropriate?
- **Overall**: Is this recipe approachable for a home cook?

---

## Additional Modes

**Shopping list** (when asked): Generate a Google Keep-ready list with tick boxes and the ingredient emojis. Group by supermarket section in this order: vegetables → dairy → meat → beverages → staples & spices.

Example:
```
☐ 🍖 Pork belly (1200 g)
☐ 🍷 Shaoxing rice wine (500 ml)
```

**German translation** (when asked): Translate the full recipe into German. Adapt ingredients to what's available in German supermarkets (e.g. replace Kosher salt with Meersalz, adjust cup measures to ml/g).
