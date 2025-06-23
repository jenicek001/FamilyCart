from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.models import User

router = APIRouter()

class ItemCategorizationRequest(BaseModel):
    item_name: str

class ItemCategorizationResponse(BaseModel):
    category_name: str

class IconSuggestionRequest(BaseModel):
    item_name: str
    category_name: Optional[str] = None

class IconSuggestionResponse(BaseModel):
    icon_name: str # e.g., 'shopping-cart', 'milk', 'apple'

# Configure Google Gemini client
if settings.GOOGLE_API_KEY:
    genai.configure(api_key=settings.GOOGLE_API_KEY)

@router.post("/ai/categorize-item", response_model=ItemCategorizationResponse)
async def categorize_item(
    request: ItemCategorizationRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Suggests a category for a given shopping list item name using Google Gemini.
    """
    if not settings.GOOGLE_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Google API key is not configured on the server.",
        )

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        You are an expert at organizing shopping lists.
        Based on the item name, suggest a single, concise category.
        The category should be a common supermarket category (e.g., "Produce", "Dairy & Eggs", "Meat & Seafood", "Bakery", "Pantry", "Frozen Foods", "Beverages", "Household").
        Return only the category name, with no extra text or punctuation.

        Item: "{request.item_name}"
        Category:
        """

        response = model.generate_content(prompt)
        category = response.text.strip()
        return ItemCategorizationResponse(category_name=category)
    except Exception as e:
        print(f"Error calling Google Gemini: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get category suggestion from AI."
        )

@router.post("/ai/suggest-icon", response_model=IconSuggestionResponse)
async def suggest_icon(
    request: IconSuggestionRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Suggests a Lucide icon name for a given shopping list item using Google Gemini.
    """
    if not settings.GOOGLE_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Google API key is not configured on the server.",
        )

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        You are an expert in UI design and iconography.
        Based on the item name and its category, suggest a single, relevant icon name from the 'lucide-react' icon library.
        Return only the icon name in kebab-case (e.g., 'shopping-cart', 'milk', 'beef', 'apple'). Do not include any extra text, explanation, or punctuation.

        Here are some examples:
        - Item: "Milk", Category: "Dairy & Eggs" -> milk
        - Item: "Sirloin Steak", Category: "Meat & Seafood" -> beef
        - Item: "Granny Smith Apples", Category: "Produce" -> apple
        - Item: "Sourdough Bread", Category: "Bakery" -> bread
        - Item: "Dish Soap", Category: "Household" -> soap
        - Item: "Paper Towels", Category: "Household" -> paperclip

        Item: "{request.item_name}"
        Category: "{request.category_name or ''}"
        Icon name:
        """

        response = model.generate_content(prompt)
        icon_name = response.text.strip()
        return IconSuggestionResponse(icon_name=icon_name)
    except Exception as e:
        print(f"Error calling Google Gemini: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get icon suggestion from AI."
        )

# This was the original prompt for item categorization created by Firebase Studio:
# const prompt = ai.definePrompt({
#  name: 'categorizeItemPrompt',
#  input: {schema: CategorizeItemInputSchema},
#  output: {schema: CategorizeItemOutputSchema},
#  prompt: `You are a shopping list expert. Given the item description, you will categorize the item into one of the following categories: Produce, Dairy, Meat, Bakery, Frozen, Pantry, Beverages, Personal Care, Household, Other. Return ONLY the category. Item Description: {{{itemDescription}}}`,
# });

# This was the original prompt for item icon generation:
# const prompt = ai.definePrompt({
#  name: 'suggestIconPrompt',
#  input: {schema: SuggestIconInputSchema},
#  output: {schema: SuggestIconOutputSchema},
#  prompt: `You are an expert in suggesting icons for shopping list items. Based on the category of the item provided, suggest an appropriate icon name and, if possible, a data URI for the icon. Category: {{{itemCategory}}}`
# });
