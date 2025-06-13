"""
Simple utility to view all saved CV data in the database.
"""

from db import get_engine, get_session, ApplicantProfile, ApplicationDetail

def view_all_data():
    """Display all saved CV data from the database."""
    engine = get_engine()
    session = get_session(engine)
    
    try:
        # Get all profiles and applications
        profiles = session.query(ApplicantProfile).all()
        applications = session.query(ApplicationDetail).all()
        
        print("=" * 60)
        print("📊 SAVED CV DATA IN DATABASE")
        print("=" * 60)
        
        if not profiles:
            print("❌ No data found in database.")
            return
        
        for profile in profiles:
            print(f"\n👤 APPLICANT ID: {profile.applicant_id}")
            print(f"   Name: {profile.first_name or 'N/A'} {profile.last_name or ''}")
            print(f"   Phone: {profile.phone_number or 'N/A'}")
            print(f"   Address: {profile.address or 'N/A'}")
            print(f"   Date of Birth: {profile.date_of_birth or 'N/A'}")
            
            # Find applications for this profile
            profile_applications = [app for app in applications if app.applicant_id == profile.applicant_id]
            
            if profile_applications:
                print(f"\n   📋 APPLICATIONS ({len(profile_applications)}):")
                for app in profile_applications:
                    print(f"      • ID: {app.detail_id}")
                    print(f"        Role: {app.application_role or 'N/A'}")
                    print(f"        CV Path: {app.cv_path or 'N/A'}")
            else:
                print("   📋 No applications found for this profile.")
            
            print("-" * 40)
        
        print(f"\n📈 SUMMARY:")
        print(f"   Total Profiles: {len(profiles)}")
        print(f"   Total Applications: {len(applications)}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")
    finally:
        session.close()

if __name__ == '__main__':
    view_all_data()
