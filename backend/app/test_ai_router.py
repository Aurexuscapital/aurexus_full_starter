# app/test_ai_router.py
import asyncio
from app.ai.nl_entry import route_query

async def main():
    prompts = [
        "What's my house worth at 123 Test St, Sydney?",
        "Simulate valuation if I add a pool at 123 Test St, Sydney",
        "What's the property outlook for Sydney in 2026?",
    ]

    for q in prompts:
        print(f"\n=== Prompt: {q}")
        try:
            resp = await route_query(q)

            if isinstance(resp, dict) and resp.get("intent") == "valuation":
                print("Intent:", resp.get("intent"))
                print("Summary:", resp.get("summary"))
                print("Token pricing (nav):", (resp.get("result") or {}).get("nav"))
                print("Prediction overlay:", resp.get("prediction_overlay"))
            else:
                print(resp)

        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())