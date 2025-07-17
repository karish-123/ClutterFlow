# backend/test_subjects.py
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.subject_service import subject_service

async def test_subjects():
    print("🔍 Testing subject service...")
    
    try:
        # Test the exact method called by the API
        subjects = await subject_service.get_all_subjects(include_stats=True)
        print(f"✅ get_all_subjects(include_stats=True): {len(subjects)} subjects")
        
        subjects_no_stats = await subject_service.get_all_subjects(include_stats=False)
        print(f"✅ get_all_subjects(include_stats=False): {len(subjects_no_stats)} subjects")
        
        # Print first subject to see structure
        if subjects_no_stats:
            print(f"📄 First subject: {subjects_no_stats[0]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_subjects())