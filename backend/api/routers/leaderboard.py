# # api/routers/leaderboard.py
# from fastapi import APIRouter, Depends, Request
# from slowapi import Limiter
# from slowapi.util import get_remote_address
# from core.utils import LeaderBoard, initialize_leaderboad
# import logging

# logger = logging.getLogger(__name__)

# router = APIRouter()
# limiter = Limiter(key_func=get_remote_address)


# @router.get("/leaderboard")
# @limiter.limit("5/minute")
# async def display_leaderboard(
#     request: Request
# ):
#     if not LeaderBoard.leader_board:
#         await initialize_leaderboard()
#     return LeaderBoard.leader_board