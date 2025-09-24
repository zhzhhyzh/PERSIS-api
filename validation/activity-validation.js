const Validator = require("validator");
const isEmpty = require("./is-empty");

module.exports = function validateactivityInput(data, type) {
    let errors = {};
    // data.username = !isEmpty(data.username) ? data.username : "";
    data.distance = !isEmpty(data.distance) ? data.distance : 0;
    data.duration_min = !isEmpty(data.duration_min) ? data.duration_min : 0;
    data.duration_sec = !isEmpty(data.duration_sec) ? data.duration_sec : 0;
    data.duration_hour = !isEmpty(data.duration_hour) ? data.duration_hour : 0;
    data.openq1 = !isEmpty(data.openq1) ? data.openq1 : "";
    data.openq2 = !isEmpty(data.openq2) ? data.openq2 : "";
    data.openq3 = !isEmpty(data.openq3) ? data.openq3 : "";
    data.openq4 = !isEmpty(data.openq4) ? data.openq4 : "";
    data.openq5 = !isEmpty(data.openq5) ? data.openq5 : "";
    data.openq6 = !isEmpty(data.openq6) ? data.openq6 : "";
    data.openq7 = !isEmpty(data.openq7) ? data.openq7 : "";
    data.openq8 = !isEmpty(data.openq8) ? data.openq8 : "";

    data.aType = !isEmpty(data.aType) ? data.aType : "";
    data.rDate = !isEmpty(data.rDate) ? data.rDate : new Date();

    // if (Validator.isEmpty(data.username)) {
    //     errors.username = "FIELDISREQUIRED";
    // } else {
    //     if (data.username.length > 255) errors.username = "INVALIDVALUELENGTH&255";
    // }



   if (isNaN(data.distance) || data.distance < 0) {
    errors.distance = "INVALIDDATAVALUE";
} else if (data.distance > 999999999999.99) {
    errors.distance = "INVALIDVALUELENGTH&15,2";
}


    if (Validator.isEmpty(data.aType)) {
        errors.aType = "FIELDISREQUIRED";
    } else {
        if (data.aType.length > 10) errors.aType = "INVALIDVALUELENGTH&10";
    }

    if (!Validator.isEmpty('' + data.rDate)) {
        let newDate = new Date(data.rDate);

        if (isNaN(newDate.getTime())) {
            errors.rDate = "INVALIDDATAVALUE";
        } else {
            const today = new Date();
            today.setHours(23, 59, 59, 59);
            if (newDate > today) {
                errors.rDate = "FUTUREDATE";
            }
        }
    }

    if (!Validator.isEmpty("" + data.duration_min) && isNaN(data.duration_min)) {
        errors.duration_min = "INVALIDDATAVALUE";

    } else if (data.duration_min > 999999999) {
        errors.duration_min = "INVALIDVALUELENGTH&999999999";

    }
    else if (data.duration_min < 0) {
        errors.duration_min = "INVALIDVALUELENGTHMIN&0"
    }
    if (!Validator.isEmpty("" + data.duration_sec) && isNaN(parseInt(data.duration_sec))) {
        errors.duration_sec = "INVALIDDATAVALUE";

    } else if (data.duration_sec > 999999999) {
        errors.duration_sec = "INVALIDVALUELENGTH&999999999";

    }
    else if (data.duration_sec < 0) {
        errors.duration_sec = "INVALIDVALUELENGTHMIN&0"
    }
    if (!Validator.isEmpty("" + data.duration_hour) && isNaN(parseInt(data.duration_hour))) {
        errors.duration_hour = "INVALIDDATAVALUE";

    } else if (data.duration_hour > 999999999) {
        errors.duration_hour = "INVALIDVALUELENGTH&999999999";

    }
    else if (data.duration_hour < 0) {
        errors.duration_hour = "INVALIDVALUELENGTHMIN&0"
    }

    if (data.openq1.length > 255) errors.openq1 = "INVALIDVALUELENGTH&255";
    if (data.openq2.length > 255) errors.openq2 = "INVALIDVALUELENGTH&255";
    if (data.openq3.length > 255) errors.openq3 = "INVALIDVALUELENGTH&255";
    if (data.openq4.length > 255) errors.openq4 = "INVALIDVALUELENGTH&255";
    if (data.openq5.length > 255) errors.openq5 = "INVALIDVALUELENGTH&255";
    if (data.openq6.length > 255) errors.openq6 = "INVALIDVALUELENGTH&255";
    if (data.openq7.length > 255) errors.openq7 = "INVALIDVALUELENGTH&255";
    if (data.openq8.length > 255) errors.openq8 = "INVALIDVALUELENGTH&255";

    if(data.duration_sec  == 0 && data.duration_hour  == 0 && data.duration_min  == 0){
        errors.duration_sec = "INVALIDDATAVALUE";
        errors.duration_hour = "INVALIDDATAVALUE";
        errors.duration_min= "INVALIDDATAVALUE";
    }
    return {
        errors,
        isValid: isEmpty(errors),
    };
};
