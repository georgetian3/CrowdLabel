from fastapi import status
from fastapi.routing import APIRouter
from .auth import Depends, get_current_user
from .documentedresponse import JSONDocumentedResponse, create_documentation
import schemas.users
import schemas.tasks
from services.users import user_service


router = APIRouter()
###############################################################################
availability_jdr = JSONDocumentedResponse(
    status.HTTP_200_OK,
    'The availability of the requested fields.',
    schemas.users.AvailabilityResponse,
)
@router.put('/availability',
    description='Checks the availability of a username or email. Returns `true` for a field if that field is available, `false` otherwise.',
    **create_documentation([availability_jdr])
)
async def availability(fields: schemas.users.AvailabilityRequest):
    response = schemas.users.AvailabilityResponse()
    if fields.username:
        response.username = not await user_service.username_exists(fields.username)
    if fields.email:
        response.email = not await user_service.email_exists(fields.email)
    return availability_jdr.response(response)
###############################################################################
verify_email_success_jdr = JSONDocumentedResponse(
    status.HTTP_200_OK,
    'Email sent successfully.',
    schemas.users.Email,
)
verify_email_failed_jdr = JSONDocumentedResponse(
    status.HTTP_400_BAD_REQUEST,
    'Email not sent successfully.',
    schemas.users.Email,
)
@router.post('/verify-email',
    description='Attempts to send an email containing a verification code to the provided address.',
    **create_documentation([verify_email_success_jdr, verify_email_failed_jdr])
)
async def verify_email(email: schemas.users.Email):
    if not await user_service.send_verification_email(email.email):
        return verify_email_failed_jdr.response(email)
    return verify_email_success_jdr.response(email)
###############################################################################
register_success_jdr = JSONDocumentedResponse(
    status.HTTP_201_CREATED,
    'Account successfully created. Returns all the following fields:',
    schemas.users.User
)
register_failed_jdr = JSONDocumentedResponse(
    status.HTTP_400_BAD_REQUEST,
    'Account creation failed. The field(s) that caused the failure and its corresponding error (`exists` for existing field (`username` or `email`), `format` (any field), or `wrong` (`verification_code`) is returned. Not all fields will necessarily be present. `user_type` must be one of `"requester"`, `"respondent"`, or `"admin"`',
    schemas.users.RegistrationError
)
@router.post('/register', 
    description='Register for an account. To be called after obtaining a verification code by calling `/verify-email`.',
    **create_documentation([register_success_jdr, register_failed_jdr])
)
async def register(details: schemas.users.RegistrationRequest):
    response = await user_service.create_user(details)
    if isinstance(response, dict):
        response = schemas.users.RegistrationError(**response)
        return register_failed_jdr.response(response)
    return register_success_jdr.response(response, exclude={'password_hashed'})
###############################################################################
me_jdr = JSONDocumentedResponse(
    status.HTTP_200_OK,
    'Successfully got me',
    schemas.users.User
)
@router.get('/me',
    description='Gets information for user who sent the request',
    **create_documentation([me_jdr])
)
async def get_me(current_user: schemas.users.User = Depends(get_current_user())):
    return me_jdr.response(current_user, exclude={'password_hashed'})
###############################################################################
@router.patch('/me',
    description='Updates user info'
)
async def edit_me(new_info : schemas.users.EditEmailRequest | schemas.users.EditPasswordRequest,
    current_user: schemas.users.User = Depends(get_current_user())
):
    # edit user's own details
    # TODO
    if isinstance(new_info, schemas.users.EditEmailRequest):
        await user_service.edit_user(email=new_info.new_email, password=new_info.password)
    elif isinstance(new_info, schemas.users.EditPasswordRequest):
        await user_service.edit_user(new_password=new_info.new_password, password=new_info.old_password)
###############################################################################
username_success_jdr = JSONDocumentedResponse(
    status.HTTP_200_OK,
    'Successfully found user.',
    schemas.users.User
)
username_failed_jdr = JSONDocumentedResponse(
    status.HTTP_404_NOT_FOUND,
    'User not found.',
)
@router.get('/{username}',
    description='Gets information for the specified username.',
    **create_documentation([username_success_jdr, username_failed_jdr])
)
async def get_user(username: str, current_user: schemas.users.User = Depends(get_current_user([]))):
    user = await user_service.get_user(username)
    if not user:
        return username_failed_jdr.response()
    return username_success_jdr.response(user)

###############################################################################
transaction_succeeded_hdr = JSONDocumentedResponse(
    status.HTTP_200_OK,
    'Transaction succeeded',
)
transaction_failed_hdr = JSONDocumentedResponse(
    status.HTTP_400_BAD_REQUEST,
    'Transaction failed',
    schemas.tasks.ErrorResponse
)
@router.post('/me/credits',
    description='Adds (positive amount) or subtracts (negative amount) from the credits',
    **create_documentation([transaction_succeeded_hdr, transaction_failed_hdr])
)
async def edit_credits(
    request: schemas.users.TransactionRequest,
    current_user: schemas.users.User = Depends(get_current_user())
):
    response = await user_service.handle_transaction(request, current_user)
    if isinstance(response, str):
        return transaction_failed_hdr.response(
            schemas.tasks.ErrorResponse(error=response)
        )
    return transaction_succeeded_hdr.response()