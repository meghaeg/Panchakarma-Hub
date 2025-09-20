const { MongoClient } = require('mongodb');
const { v4: uuidv4 } = require('uuid');

// MongoDB connection
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb+srv://your-connection-string';
const DB_NAME = process.env.DB_NAME || 'panchakarma_db';

let cachedClient = null;
let cachedDb = null;

async function connectToDatabase() {
    if (cachedClient && cachedDb) {
        return { client: cachedClient, db: cachedDb };
    }

    try {
        const client = new MongoClient(MONGODB_URI, {
            serverSelectionTimeoutMS: 5000, // 5 second timeout
            connectTimeoutMS: 5000,
            socketTimeoutMS: 5000,
        });
        
        await client.connect();
        const db = client.db(DB_NAME);
        
        cachedClient = client;
        cachedDb = db;
        
        return { client, db };
    } catch (error) {
        console.error('MongoDB connection error:', error);
        // Return null instead of throwing to allow fallback responses
        return { client: null, db: null };
    }
}

// Helper function to generate IDs
function generateId(prefix) {
    return `${prefix}${Date.now()}${Math.random().toString(36).substr(2, 5).toUpperCase()}`;
}

// Helper function to find patient by name
async function findPatientByName(db, patientName) {
    const patients = await db.collection('patients').find({
        name: { $regex: patientName, $options: 'i' }
    }).toArray();
    
    if (patients.length === 0) {
        return null;
    } else if (patients.length === 1) {
        return patients[0];
    } else {
        // Return the first match if multiple found
        return patients[0];
    }
}

// Helper function to find doctor by name
async function findDoctorByName(db, doctorName, centreId = null) {
    let query = {
        name: { $regex: doctorName, $options: 'i' },
        status: 'active'
    };
    
    if (centreId) {
        query.centre_id = centreId;
    }
    
    const doctors = await db.collection('doctors').find(query).toArray();
    
    if (doctors.length === 0) {
        return null;
    } else if (doctors.length === 1) {
        return doctors[0];
    } else {
        // Return the first match if multiple found
        return doctors[0];
    }
}

// Helper function to check doctor availability
async function checkDoctorAvailability(db, doctorId, date) {
    const appointments = await db.collection('appointments').find({
        doctor_id: doctorId,
        appointment_date: {
            $gte: new Date(date + 'T00:00:00.000Z'),
            $lt: new Date(date + 'T23:59:59.999Z')
        },
        status: { $in: ['confirmed', 'pending_approval'] }
    }).toArray();
    
    return appointments.length === 0;
}

// Helper function to get available beds
async function getAvailableBeds(db, centreId, bedType = null) {
    let query = {
        centre_id: centreId,
        status: 'available'
    };
    
    if (bedType) {
        // Map room types to bed types
        const bedTypeMapping = {
            'general ward': 'general_ward',
            'normal room': 'special_room',
            'VIP room': 'special_room',
            'special room': 'special_room',
            'panchakarma therapy': 'panchakarma_therapy'
        };
        
        if (bedTypeMapping[bedType.toLowerCase()]) {
            query.bed_type = bedTypeMapping[bedType.toLowerCase()];
        }
    }
    
    return await db.collection('beds').find(query).toArray();
}

// Helper function to allocate bed
async function allocateBed(db, bedId, patientId, patientName) {
    const result = await db.collection('beds').updateOne(
        { bed_id: bedId, status: 'available' },
        {
            $set: {
                status: 'occupied',
                current_patient_id: patientId,
                current_patient_name: patientName,
                check_in_date: new Date(),
                updated_at: new Date()
            }
        }
    );
    
    return result.modifiedCount > 0;
}

// Main Lambda handler
exports.handler = async (event, context) => {
    console.log('Event:', JSON.stringify(event, null, 2));
    
    const { request, session } = event;
    const intentName = request.intent ? request.intent.name : request.type;
    
    try {
        const { db } = await connectToDatabase();
        
        // Check if database connection is available
        if (!db) {
            console.log('Database not available, using fallback responses');
            return getFallbackResponse(intentName);
        }
        
        switch (intentName) {
            case 'AddDoctorIntent':
                return await handleAddDoctor(db, request.intent);
            
            case 'AssignDoctorIntent':
                return await handleAssignDoctor(db, request.intent);
            
            case 'CheckBedIntent':
                return await handleCheckBed(db, request.intent);
            
            case 'AllocateRoomIntent':
                return await handleAllocateRoom(db, request.intent);
            
            case 'GetCentreStatusIntent':
                return await handleGetCentreStatus(db, request.intent);
            
            case 'LaunchRequest':
                return {
                    version: '1.0',
                    response: {
                        outputSpeech: {
                            type: 'PlainText',
                            text: 'Welcome to Panchakarma Manager. I can help you manage doctors, assign patients, and handle bed allocation. What would you like to do?'
                        },
                        shouldEndSession: false
                    }
                };
            
            case 'AMAZON.HelpIntent':
                return {
                    version: '1.0',
                    response: {
                        outputSpeech: {
                            type: 'PlainText',
                            text: 'I can help you with: Adding certified doctors, assigning doctors to patients, checking bed availability, and allocating rooms. Just tell me what you need!'
                        },
                        shouldEndSession: false
                    }
                };
            
            default:
                return {
                    version: '1.0',
                    response: {
                        outputSpeech: {
                            type: 'PlainText',
                            text: 'I didn\'t understand that. Please try again or say help for assistance.'
                        },
                        shouldEndSession: false
                    }
                };
        }
    } catch (error) {
        console.error('Error:', error);
        return {
            version: '1.0',
            response: {
                outputSpeech: {
                    type: 'PlainText',
                    text: 'Sorry, I encountered an error. Please try again later.'
                },
                shouldEndSession: true
            }
        };
    }
};

// Fallback responses when database is not available
function getFallbackResponse(intentName) {
    switch (intentName) {
        case 'AddDoctorIntent':
            return {
                version: '1.0',
                response: {
                    outputSpeech: {
                        type: 'PlainText',
                        text: 'I\'m currently unable to connect to the database. Please check your connection and try again later.'
                    },
                    shouldEndSession: false
                }
            };
        
        case 'AssignDoctorIntent':
            return {
                version: '1.0',
                response: {
                    outputSpeech: {
                        type: 'PlainText',
                        text: 'I\'m currently unable to access patient records. Please check your connection and try again later.'
                    },
                    shouldEndSession: false
                }
            };
        
        case 'CheckBedIntent':
            return {
                version: '1.0',
                response: {
                    outputSpeech: {
                        type: 'PlainText',
                        text: 'I\'m currently unable to check bed availability. Please check your connection and try again later.'
                    },
                    shouldEndSession: false
                }
            };
        
        case 'AllocateRoomIntent':
            return {
                version: '1.0',
                response: {
                    outputSpeech: {
                        type: 'PlainText',
                        text: 'I\'m currently unable to allocate rooms. Please check your connection and try again later.'
                    },
                    shouldEndSession: false
                }
            };
        
        case 'GetCentreStatusIntent':
            return {
                version: '1.0',
                response: {
                    outputSpeech: {
                        type: 'PlainText',
                        text: 'I\'m currently unable to access centre status. Please check your connection and try again later.'
                    },
                    shouldEndSession: false
                }
            };
        
        case 'LaunchRequest':
            return {
                version: '1.0',
                response: {
                    outputSpeech: {
                        type: 'PlainText',
                        text: 'Welcome to Panchakarma Manager. I can help you manage doctors, assign patients, and handle bed allocation. Note: Database connection is currently unavailable.'
                    },
                    shouldEndSession: false
                }
            };
        
        default:
            return {
                version: '1.0',
                response: {
                    outputSpeech: {
                        type: 'PlainText',
                        text: 'I\'m currently experiencing connection issues. Please try again later.'
                    },
                    shouldEndSession: false
                }
            };
    }
}

// Add Doctor Intent Handler
async function handleAddDoctor(db, intent) {
    const slots = intent.slots;
    const doctorName = slots.DoctorName ? slots.DoctorName.value : null;
    const certificationStatus = slots.CertificationStatus ? slots.CertificationStatus.value : null;
    
    if (!doctorName) {
        return {
            version: '1.0',
            response: {
                outputSpeech: {
                    type: 'PlainText',
                    text: 'I need the doctor\'s name to add them to the center.'
                },
                shouldEndSession: false
            }
        };
    }
    
    // Check if doctor is certified
    const isCertified = certificationStatus && 
        (certificationStatus.toLowerCase().includes('certified') || 
         certificationStatus.toLowerCase().includes('verified'));
    
    if (!isCertified) {
        return {
            version: '1.0',
            response: {
                outputSpeech: {
                    type: 'PlainText',
                    text: 'Cannot add doctor, certification not verified. Please ensure the doctor is certified before adding.'
                },
                shouldEndSession: false
            }
        };
    }
    
    try {
        // Check if doctor already exists
        const existingDoctor = await findDoctorByName(db, doctorName);
        if (existingDoctor) {
            return {
                version: '1.0',
                response: {
                    outputSpeech: {
                        type: 'PlainText',
                        text: `Doctor ${doctorName} already exists in the system.`
                    },
                    shouldEndSession: false
                }
            };
        }
        
        // Get any centre from the database or use a default
        const centres = await db.collection('centres').find({}).limit(1).toArray();
        const centreId = centres.length > 0 ? centres[0].centre_id : 'CENTRE001';
        
        // Create new doctor
        const doctorData = {
            doctor_id: generateId('DOC'),
            centre_id: centreId,
            name: doctorName,
            email: `${doctorName.toLowerCase().replace(/\s+/g, '.')}@panchakarma.com`,
            phone: '0000000000',
            specialization: 'Panchakarma Therapy',
            experience: '5',
            qualification: 'BAMS',
            license_number: `LIC${Date.now()}`,
            password: '$2b$12$dummy.hash.for.demo', // In production, generate proper hash
            created_at: new Date(),
            status: 'active',
            available_sessions: ['09:00-10:00', '10:00-11:00', '11:00-12:00', '14:00-15:00', '15:00-16:00', '16:00-17:00'],
            working_days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
            is_certified: true,
            certification_verified: true
        };
        
        await db.collection('doctors').insertOne(doctorData);
        
        return {
            version: '1.0',
            response: {
                outputSpeech: {
                    type: 'PlainText',
                    text: `Successfully added certified doctor ${doctorName} to the center. Doctor ID is ${doctorData.doctor_id}.`
                },
                shouldEndSession: false
            }
        };
    } catch (error) {
        console.error('Error adding doctor:', error);
        return {
            version: '1.0',
            response: {
                outputSpeech: {
                    type: 'PlainText',
                    text: 'Sorry, I encountered an error while adding the doctor. Please try again.'
                },
                shouldEndSession: false
            }
        };
    }
}

// Assign Doctor Intent Handler
async function handleAssignDoctor(db, intent) {
    const slots = intent.slots;
    const patientName = slots.PatientName ? slots.PatientName.value : null;
    const doctorName = slots.DoctorName ? slots.DoctorName.value : null;
    
    if (!patientName) {
        return {
            version: '1.0',
            response: {
                outputSpeech: {
                    type: 'PlainText',
                    text: 'I need the patient\'s name to assign a doctor.'
                },
                shouldEndSession: false
            }
        };
    }
    
    try {
        // Find patient
        const patient = await findPatientByName(db, patientName);
        if (!patient) {
            return {
                version: '1.0',
                response: {
                    outputSpeech: {
                        type: 'PlainText',
                        text: `Patient ${patientName} not found in the system.`
                    },
                    shouldEndSession: false
                }
            };
        }
        
        let doctor = null;
        
        if (doctorName) {
            // Find specific doctor
            doctor = await findDoctorByName(db, doctorName, patient.centre_id);
            if (!doctor) {
                return {
                    version: '1.0',
                    response: {
                        outputSpeech: {
                            type: 'PlainText',
                            text: `Doctor ${doctorName} not found or not available at this center.`
                        },
                        shouldEndSession: false
                    }
                };
            }
        } else {
            // Find available doctor
            const doctors = await db.collection('doctors').find({
                centre_id: patient.centre_id,
                status: 'active'
            }).toArray();
            
            if (doctors.length === 0) {
                return {
                    version: '1.0',
                    response: {
                        outputSpeech: {
                            type: 'PlainText',
                            text: 'No doctors available at this center.'
                        },
                        shouldEndSession: false
                    }
                };
            }
            
            // Find first available doctor
            for (const doc of doctors) {
                const isAvailable = await checkDoctorAvailability(db, doc.doctor_id, new Date().toISOString().split('T')[0]);
                if (isAvailable) {
                    doctor = doc;
                    break;
                }
            }
            
            if (!doctor) {
                return {
                    version: '1.0',
                    response: {
                        outputSpeech: {
                            type: 'PlainText',
                            text: 'No doctors are available for assignment at this time.'
                        },
                        shouldEndSession: false
                    }
                };
            }
        }
        
        // Check if doctor is available
        const isAvailable = await checkDoctorAvailability(db, doctor.doctor_id, new Date().toISOString().split('T')[0]);
        if (!isAvailable) {
            return {
                version: '1.0',
                response: {
                    outputSpeech: {
                        type: 'PlainText',
                        text: `Doctor ${doctor.name} is not available for assignment today.`
                    },
                    shouldEndSession: false
                }
            };
        }
        
        // Create appointment
        const appointmentData = {
            appointment_id: generateId('APT'),
            patient_id: patient.patient_id,
            centre_id: patient.centre_id,
            doctor_id: doctor.doctor_id,
            therapy_type: 'General Consultation',
            appointment_date: new Date(),
            time_slot: '10:00-11:00', // Default time slot
            status: 'confirmed',
            notes: 'Assigned via Alexa voice command',
            created_at: new Date(),
            updated_at: new Date(),
            assigned_doctor: doctor.name
        };
        
        await db.collection('appointments').insertOne(appointmentData);
        
        return {
            version: '1.0',
            response: {
                outputSpeech: {
                    type: 'PlainText',
                    text: `Successfully assigned doctor ${doctor.name} to patient ${patientName}. Appointment ID is ${appointmentData.appointment_id}.`
                },
                shouldEndSession: false
            }
        };
    } catch (error) {
        console.error('Error assigning doctor:', error);
        return {
            version: '1.0',
            response: {
                outputSpeech: {
                    type: 'PlainText',
                    text: 'Sorry, I encountered an error while assigning the doctor. Please try again.'
                },
                shouldEndSession: false
            }
        };
    }
}

// Check Bed Intent Handler
async function handleCheckBed(db, intent) {
    const slots = intent.slots;
    const timePeriod = slots.TimePeriod ? slots.TimePeriod.value : 'today';
    
    try {
        // For demo purposes, using a default centre ID
        const centreId = 'CENTRE001';
        
        const availableBeds = await getAvailableBeds(db, centreId);
        
        if (availableBeds.length === 0) {
            return {
                version: '1.0',
                response: {
                    outputSpeech: {
                        type: 'PlainText',
                        text: `No beds are available for ${timePeriod}. All beds are currently occupied.`
                    },
                    shouldEndSession: false
                }
            };
        }
        
        // Group beds by type
        const bedsByType = {};
        availableBeds.forEach(bed => {
            if (!bedsByType[bed.bed_type]) {
                bedsByType[bed.bed_type] = [];
            }
            bedsByType[bed.bed_type].push(bed);
        });
        
        let responseText = `Available beds for ${timePeriod}: `;
        Object.keys(bedsByType).forEach(type => {
            const count = bedsByType[type].length;
            const typeName = type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            responseText += `${count} ${typeName} beds, `;
        });
        
        responseText = responseText.slice(0, -2) + '.';
        
        return {
            version: '1.0',
            response: {
                outputSpeech: {
                    type: 'PlainText',
                    text: responseText
                },
                shouldEndSession: false
            }
        };
    } catch (error) {
        console.error('Error checking beds:', error);
        return {
            version: '1.0',
            response: {
                outputSpeech: {
                    type: 'PlainText',
                    text: 'Sorry, I encountered an error while checking bed availability. Please try again.'
                },
                shouldEndSession: false
            }
        };
    }
}

// Allocate Room Intent Handler
async function handleAllocateRoom(db, intent) {
    const slots = intent.slots;
    const patientName = slots.PatientName ? slots.PatientName.value : null;
    const roomType = slots.RoomType ? slots.RoomType.value : null;
    
    if (!patientName) {
        return {
            version: '1.0',
            response: {
                outputSpeech: {
                    type: 'PlainText',
                    text: 'I need the patient\'s name to allocate a room.'
                },
                shouldEndSession: false
            }
        };
    }
    
    if (!roomType) {
        return {
            version: '1.0',
            response: {
                outputSpeech: {
                    type: 'PlainText',
                    text: 'I need to know what type of room you want to allocate.'
                },
                shouldEndSession: false
            }
        };
    }
    
    try {
        // Find patient
        const patient = await findPatientByName(db, patientName);
        if (!patient) {
            return {
                version: '1.0',
                response: {
                    outputSpeech: {
                        type: 'PlainText',
                        text: `Patient ${patientName} not found in the system.`
                    },
                    shouldEndSession: false
                }
            };
        }
        
        // Get available beds of requested type
        const availableBeds = await getAvailableBeds(db, patient.centre_id, roomType);
        
        if (availableBeds.length === 0) {
            return {
                version: '1.0',
                response: {
                    outputSpeech: {
                        type: 'PlainText',
                        text: `Requested ${roomType} room not available, please choose another type.`
                    },
                    shouldEndSession: false
                }
            };
        }
        
        // Allocate the first available bed
        const bed = availableBeds[0];
        const success = await allocateBed(db, bed.bed_id, patient.patient_id, patient.name);
        
        if (success) {
            return {
                version: '1.0',
                response: {
                    outputSpeech: {
                        type: 'PlainText',
                        text: `Successfully allocated ${roomType} room ${bed.room_number} to patient ${patientName}. Bed ID is ${bed.bed_id}.`
                    },
                    shouldEndSession: false
                }
            };
        } else {
            return {
                version: '1.0',
                response: {
                    outputSpeech: {
                        type: 'PlainText',
                        text: 'Sorry, I was unable to allocate the room. Please try again.'
                    },
                    shouldEndSession: false
                }
            };
        }
    } catch (error) {
        console.error('Error allocating room:', error);
        return {
            version: '1.0',
            response: {
                outputSpeech: {
                    type: 'PlainText',
                    text: 'Sorry, I encountered an error while allocating the room. Please try again.'
                },
                shouldEndSession: false
            }
        };
    }
}

// Get Centre Status Intent Handler
async function handleGetCentreStatus(db, intent) {
    try {
        // Get any centre from the database (since we don't have a specific centre ID)
        const centres = await db.collection('centres').find({}).limit(1).toArray();
        let centre = null;
        
        if (centres.length > 0) {
            centre = centres[0];
        }
        
        // Get statistics (without filtering by centre_id since we want overall stats)
        const totalDoctors = await db.collection('doctors').countDocuments({ status: 'active' });
        const totalPatients = await db.collection('patients').countDocuments({ status: 'active' });
        const totalBeds = await db.collection('beds').countDocuments({});
        const availableBeds = await db.collection('beds').countDocuments({ status: 'available' });
        const occupiedBeds = await db.collection('beds').countDocuments({ status: 'occupied' });
        
        const centreName = centre ? centre.name : 'Panchakarma Centre';
        const responseText = `Centre ${centreName} status: ${totalDoctors} active doctors, ${totalPatients} patients, ${totalBeds} total beds with ${availableBeds} available and ${occupiedBeds} occupied.`;
        
        return {
            version: '1.0',
            response: {
                outputSpeech: {
                    type: 'PlainText',
                    text: responseText
                },
                shouldEndSession: false
            }
        };
    } catch (error) {
        console.error('Error getting centre status:', error);
        return {
            version: '1.0',
            response: {
                outputSpeech: {
                    type: 'PlainText',
                    text: 'Sorry, I encountered an error while getting centre status. Please try again.'
                },
                shouldEndSession: false
            }
        };
    }
}
