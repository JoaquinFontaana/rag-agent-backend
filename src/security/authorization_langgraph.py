# from langgraph_sdk import Auth
# from src.security.auth_langgraph import auth

# #...
# def _get_thread_filter(ctx: Auth.types.AuthContext) -> dict:
#     """
#     Get thread filter based on user role.
#     
#     - ADMIN: Can see ALL threads (customer service)
#     - USER: Can only see their own threads
#     """
#     # Check if user has admin role (from JWT payload)
#     user_role = getattr(ctx.user, "role", "user")
#     
#     if user_role == "admin":
#         return {}  # No filter - admin sees all threads
#     
#     # Regular users only see their own threads
#     return {"owner": ctx.user.identity}


# @auth.on.threads.create
# async def on_threads_create(
#     ctx: Auth.types.AuthContext,
#     value: Auth.types.on.threads.create.value
# ) -> dict:
#     """Add owner when creating threads."""
#     # Always add owner metadata (even for admins)
#     filters = {"owner": ctx.user.identity}
#     metadata = value.setdefault("metadata", {})
#     metadata.update(filters)
#     
#     return filters


# @auth.on.threads.read
# async def on_thread_read(
#     ctx: Auth.types.AuthContext,
#     value: Auth.types.on.threads.read.value,
# ) -> dict:
#     """
#     Users can read their own threads.
#     Admins can read ANY thread (for customer service).
#     """
#     return _get_thread_filter(ctx)


# @auth.on.threads.update
# async def on_thread_update(
#     ctx: Auth.types.AuthContext,
#     value: Auth.types.on.threads.update.value,
# ) -> dict:
#     """
#     Users can update their own threads.
#     Admins can update ANY thread (for human handoff).
#     
#     This includes:
#     - Updating thread state via update_state API
#     - Resuming from interrupts (human handoff)
#     - Time travel operations
#     """
#     return _get_thread_filter(ctx)


# @auth.on.threads.search
# async def on_thread_search(
#     ctx: Auth.types.AuthContext,
#     value: Auth.types.on.threads.search.value,
# ) -> dict:
#     """
#     Users see only their threads.
#     Admins see ALL threads (for customer service dashboard).
#     """
#     return _get_thread_filter(ctx)
