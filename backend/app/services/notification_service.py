from app.schemas.shopping_list import ShoppingListRead


async def send_list_invitation_email(
    to_email: str,
    list_data: dict,
    inviter_email: str,
) -> None:
    """
    Send an email invitation to a user to join a shared shopping list.

    Args:
        to_email (str): Email of the user to invite.
        list_data (dict): JSON-serializable shopping list data.
        inviter_email (str): Email of the user sending the invitation.
    """
    # TODO: Integrate with actual email service (e.g., SMTP, SendGrid)
    # Reason: Placeholder implementation for email notifications.
    print(
        f"[Notification] Email sent to {to_email}: You have been invited by {inviter_email} to collaborate on list '{list_data.get('name')}'."
    )
