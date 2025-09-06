from datetime import datetime, timedelta
from typing import Dict, List, Any

class DetoxPlans:
    """Detox therapy plans and scheduling system"""
    
    # Time slots for each day
    TIME_SLOTS = {
        'morning': {'time': '07:00', 'name': 'Morning'},
        'breakfast': {'time': '09:00', 'name': 'Breakfast'},
        'lunch': {'time': '13:00', 'name': 'Lunch'},
        'evening': {'time': '17:00', 'name': 'Evening'},
        'dinner': {'time': '20:00', 'name': 'Dinner'},
        'therapy': {'time': '21:00', 'name': 'Therapy'}
    }
    
    # Safety precautions
    SAFETY_PRECAUTIONS = {
        'general': [
            "Avoid heavy exercise during detox",
            "Stay hydrated throughout the day",
            "No junk food or processed foods",
            "Get adequate sleep (7-8 hours)",
            "Listen to your body and rest when needed"
        ],
        'diabetes': [
            "Monitor blood sugar 3-4 times daily",
            "Avoid fruit-only or juice-only meals",
            "Always carry emergency snack for hypoglycemia",
            "Include protein in every meal",
            "Check blood sugar before and after meals"
        ]
    }
    
    @staticmethod
    def get_weight_loss_short_plan() -> Dict[str, Any]:
        """7-day weight loss detox plan"""
        plan = {
            'name': 'Weight Loss - Short (7 Days)',
            'duration': 7,
            'type': 'weight_loss',
            'precautions': DetoxPlans.SAFETY_PRECAUTIONS['general'],
            'schedule': {}
        }
        
        # Day-wise schedule
        for day in range(1, 8):
            plan['schedule'][f'day_{day}'] = {
                'morning': 'Warm lemon water with honey',
                'breakfast': 'Seasonal fruits (apple, papaya, berries)',
                'lunch': 'Vegetable soup with minimal salt',
                'evening': 'Herbal tea (green tea or chamomile)',
                'dinner': 'Steamed vegetables with dal water',
                'therapy': 'Light walk (30 minutes) or yoga'
            }
        
        return plan
    
    @staticmethod
    def get_weight_loss_full_plan() -> Dict[str, Any]:
        """14-day weight loss detox plan with phases"""
        plan = {
            'name': 'Weight Loss - Full (14 Days)',
            'duration': 14,
            'type': 'weight_loss',
            'precautions': DetoxPlans.SAFETY_PRECAUTIONS['general'],
            'schedule': {}
        }
        
        # Phase 1 (Days 1-4): Light meals + 1 liquid day
        for day in range(1, 5):
            if day == 2:  # Liquid day
                plan['schedule'][f'day_{day}'] = {
                    'morning': 'Warm lemon water',
                    'breakfast': 'Coconut water',
                    'lunch': 'Vegetable soup (liquid only)',
                    'evening': 'Herbal tea',
                    'dinner': 'Fruit smoothie',
                    'therapy': 'Meditation (20 minutes)'
                }
            else:
                plan['schedule'][f'day_{day}'] = {
                    'morning': 'Warm lemon water with honey',
                    'breakfast': 'Seasonal fruits',
                    'lunch': 'Light vegetable soup',
                    'evening': 'Herbal tea',
                    'dinner': 'Steamed vegetables',
                    'therapy': 'Light yoga (30 minutes)'
                }
        
        # Phase 2 (Days 5-8): Probiotics, soups, mono meal
        for day in range(5, 9):
            plan['schedule'][f'day_{day}'] = {
                'morning': 'Probiotic drink (buttermilk)',
                'breakfast': 'Oats porridge with fruits',
                'lunch': 'Moong dal soup with vegetables',
                'evening': 'Herbal tea with ginger',
                'dinner': 'Mono meal (only one type of grain)',
                'therapy': 'Walking + meditation (45 minutes)'
            }
        
        # Phase 3 (Days 9-12): Balanced millets, dal, oats, paneer
        for day in range(9, 13):
            plan['schedule'][f'day_{day}'] = {
                'morning': 'Warm water with lemon',
                'breakfast': 'Millet porridge with nuts',
                'lunch': 'Brown rice with dal and vegetables',
                'evening': 'Herbal tea',
                'dinner': 'Paneer with steamed vegetables',
                'therapy': 'Yoga + light exercise (1 hour)'
            }
        
        # Phase 4 (Days 13-14): Transition to sustainable diet
        for day in range(13, 15):
            plan['schedule'][f'day_{day}'] = {
                'morning': 'Warm lemon water',
                'breakfast': 'Balanced breakfast (oats + fruits)',
                'lunch': 'Normal meal (rice + dal + vegetables)',
                'evening': 'Herbal tea',
                'dinner': 'Light dinner (soup + salad)',
                'therapy': 'Regular exercise routine'
            }
        
        return plan
    
    @staticmethod
    def get_diabetes_short_plan() -> Dict[str, Any]:
        """7-day diabetes detox plan"""
        plan = {
            'name': 'Diabetes - Short (7 Days)',
            'duration': 7,
            'type': 'diabetes',
            'precautions': DetoxPlans.SAFETY_PRECAUTIONS['general'] + DetoxPlans.SAFETY_PRECAUTIONS['diabetes'],
            'schedule': {}
        }
        
        # Day-wise schedule for diabetes
        for day in range(1, 8):
            plan['schedule'][f'day_{day}'] = {
                'morning': 'Warm water with cinnamon',
                'breakfast': 'Oats with nuts and seeds',
                'lunch': 'Moong dal soup with vegetables',
                'evening': 'Herbal tea (fenugreek)',
                'dinner': 'Steamed vegetables with dal',
                'therapy': 'Light walk (30 minutes)'
            }
        
        return plan
    
    @staticmethod
    def get_diabetes_full_plan() -> Dict[str, Any]:
        """14-day diabetes detox plan with phases"""
        plan = {
            'name': 'Diabetes - Full (14 Days)',
            'duration': 14,
            'type': 'diabetes',
            'precautions': DetoxPlans.SAFETY_PRECAUTIONS['general'] + DetoxPlans.SAFETY_PRECAUTIONS['diabetes'],
            'schedule': {}
        }
        
        # Phase 1 (Days 1-4): Oats, sprouts, khichdi, 1 controlled liquid day
        for day in range(1, 5):
            if day == 3:  # Controlled liquid day
                plan['schedule'][f'day_{day}'] = {
                    'morning': 'Warm water with cinnamon',
                    'breakfast': 'Vegetable soup (liquid)',
                    'lunch': 'Dal water with minimal salt',
                    'evening': 'Herbal tea (fenugreek)',
                    'dinner': 'Fruit smoothie (low sugar)',
                    'therapy': 'Meditation (20 minutes)'
                }
            else:
                plan['schedule'][f'day_{day}'] = {
                    'morning': 'Warm water with cinnamon',
                    'breakfast': 'Oats with nuts',
                    'lunch': 'Moong dal khichdi',
                    'evening': 'Herbal tea (fenugreek)',
                    'dinner': 'Steamed vegetables with dal',
                    'therapy': 'Light walk (30 minutes)'
                }
        
        # Phase 2 (Days 5-8): Probiotics, moong dal, quinoa, mono meal
        for day in range(5, 9):
            plan['schedule'][f'day_{day}'] = {
                'morning': 'Probiotic drink (buttermilk)',
                'breakfast': 'Quinoa porridge with nuts',
                'lunch': 'Moong dal with vegetables',
                'evening': 'Herbal tea (fenugreek)',
                'dinner': 'Mono meal (only one type of grain)',
                'therapy': 'Walking + meditation (45 minutes)'
            }
        
        # Phase 3 (Days 9-12): Healing: balanced thali, sprouts, paneer, oats
        for day in range(9, 13):
            plan['schedule'][f'day_{day}'] = {
                'morning': 'Warm water with cinnamon',
                'breakfast': 'Oats with sprouts and nuts',
                'lunch': 'Balanced thali (rice + dal + vegetables)',
                'evening': 'Herbal tea (fenugreek)',
                'dinner': 'Paneer with steamed vegetables',
                'therapy': 'Yoga + light exercise (1 hour)'
            }
        
        # Phase 4 (Days 13-14): Transition: roti/dal/sabzi/curd, soups, khichdi
        for day in range(13, 15):
            plan['schedule'][f'day_{day}'] = {
                'morning': 'Warm water with cinnamon',
                'breakfast': 'Oats with fruits and nuts',
                'lunch': 'Roti with dal and sabzi',
                'evening': 'Herbal tea (fenugreek)',
                'dinner': 'Khichdi with curd',
                'therapy': 'Regular exercise routine'
            }
        
        return plan
    
    @staticmethod
    def get_plan_by_type(plan_type: str) -> Dict[str, Any]:
        """Get detox plan by type"""
        plans = {
            'weight_loss_short': DetoxPlans.get_weight_loss_short_plan(),
            'weight_loss_full': DetoxPlans.get_weight_loss_full_plan(),
            'diabetes_short': DetoxPlans.get_diabetes_short_plan(),
            'diabetes_full': DetoxPlans.get_diabetes_full_plan()
        }
        return plans.get(plan_type, {})
    
    @staticmethod
    def generate_schedule(plan_type: str, start_date: str, therapy_time: str = "10:00") -> Dict[str, Any]:
        """Generate a complete schedule for a detox plan"""
        plan = DetoxPlans.get_plan_by_type(plan_type)
        if not plan:
            return {}
        
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        schedule = {
            'plan_info': {
                'name': plan['name'],
                'type': plan['type'],
                'duration': plan['duration'],
                'precautions': plan['precautions'],
                'start_date': start_date,
                'therapy_time': therapy_time
            },
            'daily_schedules': {}
        }
        
        # Generate daily schedules (skipping Sundays)
        day_count = 0
        current_date = start_dt
        day_number = 1
        
        while day_count < plan['duration']:
            day_of_week = current_date.strftime('%A').lower()
            
            # Skip Sundays - don't count them in the duration
            if day_of_week == 'sunday':
                current_date += timedelta(days=1)
                continue
            
            day_key = f'day_{day_number}'
            
            schedule['daily_schedules'][day_key] = {
                'date': current_date.strftime('%Y-%m-%d'),
                'day_number': day_number,
                'slots': {}
            }
            
            # Map time slots with actual times
            for slot_key, slot_info in DetoxPlans.TIME_SLOTS.items():
                if slot_key in plan['schedule'][day_key]:
                    schedule['daily_schedules'][day_key]['slots'][slot_key] = {
                        'time': slot_info['time'],
                        'name': slot_info['name'],
                        'activity': plan['schedule'][day_key][slot_key],
                        'status': 'pending',  # pending, completed, skipped
                        'notes': '',
                        'modified_by': None,
                        'modified_at': None
                    }
            
            # Move to next day and increment counters
            current_date += timedelta(days=1)
            day_count += 1
            day_number += 1
        
        return schedule
    
    @staticmethod
    def update_slot_activity(schedule: Dict[str, Any], day: int, slot: str, 
                           new_activity: str, modified_by: str) -> Dict[str, Any]:
        """Update a specific slot activity and sync across dashboards"""
        day_key = f'day_{day}'
        if day_key in schedule['daily_schedules'] and slot in schedule['daily_schedules'][day_key]['slots']:
            schedule['daily_schedules'][day_key]['slots'][slot]['activity'] = new_activity
            schedule['daily_schedules'][day_key]['slots'][slot]['modified_by'] = modified_by
            schedule['daily_schedules'][day_key]['slots'][slot]['modified_at'] = datetime.now().isoformat()
        
        return schedule
    
    @staticmethod
    def add_slot_notes(schedule: Dict[str, Any], day: int, slot: str, 
                      notes: str, modified_by: str) -> Dict[str, Any]:
        """Add notes to a specific slot"""
        day_key = f'day_{day}'
        if day_key in schedule['daily_schedules'] and slot in schedule['daily_schedules'][day_key]['slots']:
            schedule['daily_schedules'][day_key]['slots'][slot]['notes'] = notes
            schedule['daily_schedules'][day_key]['slots'][slot]['modified_by'] = modified_by
            schedule['daily_schedules'][day_key]['slots'][slot]['modified_at'] = datetime.now().isoformat()
        
        return schedule
