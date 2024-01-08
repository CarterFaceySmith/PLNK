import express from "express";

const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const asyncHandler = require('express-async-handler');
const User = require('../models/User');

// const { registerUser, loginUser, findUser } = require('../controllers/userController');

const router = express.Router();

// @desc    Register a new user
// @route   POST /users/create
// @access  Public
router.post("/users/create", asyncHandler(async (req, res) => {
    const { name, email, password, isAdmin } = req.body;
    if (!name || !email || !password) {
        res.status(400).json({ message: "Please fill out all fields." });
    }

    const userExists = await User.findById(email);
    if (userExists) {
        res.status(400).json({ message: "User already exists." });
    }

    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);

    try {
        const user = await User.create({ name, email, hashedPassword, isAdmin });
        res.status(201).json(user);
    } catch (error) {
        res.status(400).json({ message: error.message });
    }
}));

// @desc    Login a user
// @route   POST /users/login
// @access  Public
router.post("/users/login", asyncHandler(async (req, res) => {
    const { email, password } = req.body;
    try {
        const user = await User.findById(email);
        if (User && (await bcrypt.compare(password, user.hashedPassword))) {
            res.status(200).json(user);
        }
        else {
            res.status(401).json({ message: "Invalid email or password." });
        }
    } catch (error) {
        res.status(400).json({ message: error.message });
    }
}));

// router.get("/users/find", async (req, res) => {
//   try {
//     const users = await User.find();
//     res.status(200).json(users);
//   } catch (error) {
//     res.status(404).json({ message: error.message });
//   }
// });

// @desc    Find a user
// @route   GET /users/:id
// @access  Public
router.get("/users/:id", asyncHandler(async (req, res) => {
    const { id } = req.params;
    try {
        const user = await User.findById(id);
        res.status(200).json(user);
    } catch (error) {
        res.status(404).json({ message: error.message });
    }
}));

export default router;
