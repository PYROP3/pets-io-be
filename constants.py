class constants:

    def __init__(self):
        # Requests
        # -- API
        # -- Account
        self.CREATE_ACCOUNT_REQUEST      = "/createAccount"
        self.VERIFY_ACCOUNT_REQUEST      = "/verifyAccount"
        self.AUTH_REQUEST                = "/auth"
        self.DEAUTH_REQUEST              = "/deauth"
        self.RECOVER_PASS_NONCE_REQUEST  = "/recoverPasswordNonce"
        self.RECOVER_PASS_REQUEST        = "/recoverPassword"
        self.EVENT_TRIGGERED_REQUEST     = "/eventTriggered"
        self.GET_PENDING_PETS_REQUEST    = "/getPendingPets"
        self.UPDATE_PET_PICS_REQUEST     = "/updatePetPictures"

        # Scripts
        self.SCRIPT_PATH = "script/"

        # Log storage
        self.LOG_STORAGE_PATH = "log/"

        # Error data
        self.SCRIPT_ERRORS_PATH   = self.SCRIPT_PATH + "errorCodes.json"

        # Localization defaults
        self.DEFAULT_LOCALE = "en-us"

        # Mailer data
        self.SOURCE_EMAIL_ADDRESS = "pets.io.tcc@gmail.com"
        self.SOURCE_EMAIL_SERVICE = "gmail"
        self.SOURCE_EMAIL_HOST    = "smtp.gmail.com"

        # Mongo keys
        self.USER_NAME_KEY         = "UserName"
        self.USER_TOKEN_KEY        = "UserToken"
        self.USER_N_PETS_KEY       = "UserNPets"
        self.USER_PENDING_PETS_KEY = "UserPendingPets"
        self.USER_N_DEVICES_KEY    = "UserNDevices"
        self.USER_EMAIL_KEY        = "UserEmail"
        self.USER_PASS_KEY         = "UserPass"
        self.USER_TIMESTAMP_KEY    = "Timestamp"
        self.PET_PICTURES_KEY      = "PetPictures"
        self.DEVICE_ID_KEY         = "DeviceID"
        self.EVENT_PICTURE_KEY     = "EventPicture"
        self.EVENT_EXTRA           = "EventExtra"
        self.FCM_TOKEN_KEY         = "FCMToken"

        # Authentication info
        self.AUTH_TOKEN_LENGTH = 256
        self.AUTH_TOKEN_TYPE   = "Bearer"
        self.AUTH_TOKEN_NAME   = self.AUTH_TOKEN_TYPE + " "

        # Mongo collections
        self.MONGO_COLLECTION_USERS                = "users"
        self.MONGO_COLLECTION_SESSIONS             = "sessions"
        self.MONGO_COLLECTION_PENDING_USERS        = "pendingUsers"
        self.MONGO_COLLECTION_PETS                 = "pets"
        self.MONGO_COLLECTION_EVENTS               = "events"
        self.MONGO_COLLECTION_PENDING_RECOVER_PASS = "passwordNonces"

        self.SERVER_PORT_DEFAULT = 8080
        self.SERVER_URL_DEFAULT = "https://pets-io.herokuapp.com"

        self.SUCCESS_MSG = "Success!"
