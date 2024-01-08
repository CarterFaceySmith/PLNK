const mongoose = require('mongoose');

const userSchema = mongoose.Schema(
    {
        name: {
            type: String,
            required: [true, 'Please add a name.']
        },
        email: {
            type: String, 
            required: true,
            unique: [true, 'Please add an email.']
        },
        password: {
            type: String,
            required: [true, 'Please add a password.']
        },
        isAdmin: {
            type: Boolean,
            required: true,
            default: false
        }
    }, 
    {
        timestamps: true, toJSON: { getters: true }
    });

    module.exports = mongoose.model('User', userSchema);

    export default User;