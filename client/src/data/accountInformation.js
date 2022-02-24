export default {
    confirmPasswordRules: [v => !!v || "Please confirm your password"],
    passwordRules: [
        v => {
            const pattern = /[\s]+/;
            return !pattern.test(v) || "Your password can't contain whitespaces";
        },
        v =>
            (v || "").length >= 6 ||
            "Your password has to be at least 6 characters long",
        v => {
            const pattern = /[a-zA-Z]+/;
            return (
                pattern.test(v) || "Your password has to have at least one letter"
            );
        },
        v => {
            const pattern = /[0-9]+/;
            return (
                pattern.test(v) || "Your password has to have at least one number"
            );
        },
        v => {
            const pattern = /[\W]+/;
            return (
                pattern.test(v) ||
                "Your password has to have at least one special character"
            );
        }
    ],
};
