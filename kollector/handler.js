"use strict"

module.exports = (event, context) => {

    


    context
        .status(200)
        .succeed({"status":"ok"});
}
