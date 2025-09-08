from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.dependencies import get_current_user
from app.models import User
from app.services.ai_service import ai_service

router = APIRouter()


class ItemCategorizationRequest(BaseModel):
    item_name: str


class ItemCategorizationResponse(BaseModel):
    category_name: str


class IconSuggestionRequest(BaseModel):
    item_name: str
    category_name: Optional[str] = None


class IconSuggestionResponse(BaseModel):
    icon_name: str  # e.g., 'shopping-cart', 'milk', 'apple'


class AIProviderStatusResponse(BaseModel):
    provider_name: str
    model_name: str
    status: str
    error: Optional[str] = None
    rate_limit_detected: Optional[bool] = None
    fallback_available: Optional[bool] = None


@router.get("/ai/status", response_model=AIProviderStatusResponse)
async def get_ai_status():
    """
    Get the current AI provider status and configuration.
    """
    try:
        provider_info = ai_service.get_provider_info()
        return AIProviderStatusResponse(**provider_info)
    except Exception as e:
        return AIProviderStatusResponse(
            provider_name="unknown", model_name="unknown", status="error", error=str(e)
        )


@router.post("/ai/categorize-item", response_model=ItemCategorizationResponse)
async def categorize_item(
    request: ItemCategorizationRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Suggests a category for a given shopping list item name using the configured AI provider.
    """
    try:
        # Use the AI service with the provider pattern
        prompt = f"""
        You are an expert at organizing shopping lists.
        Based on the item name, suggest a single, concise category.
        The category should be a common supermarket category (e.g., "Produce", "Dairy & Eggs", "Meat & Seafood", "Bakery", "Pantry", "Frozen Foods", "Beverages", "Household").
        Return only the category name, with no extra text or punctuation.

        Item: "{request.item_name}"
        Category:
        """

        response = await ai_service.generate_text(prompt)
        category = response.strip()
        return ItemCategorizationResponse(category_name=category)
    except Exception as e:
        print(f"Error calling AI provider: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get category suggestion from AI."
        )


@router.post("/ai/suggest-icon", response_model=IconSuggestionResponse)
async def suggest_icon(
    request: IconSuggestionRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Suggests a Material Design icon name for a given shopping list item using the configured AI provider.
    """
    try:
        # Use the standardized AI service method for icon suggestion
        category_name = request.category_name or "General"
        icon_name = await ai_service.suggest_icon(request.item_name, category_name)
        return IconSuggestionResponse(icon_name=icon_name)
    except Exception as e:
        print(f"Error calling AI provider: {e}")
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
