const { handleAuth } = require("./auth");

exports.handler = async function (event) {
    return handleAuth(event, "register");
};
