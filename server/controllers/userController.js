const registerUser = async (req, res) => {
    const { name, email, password, isAdmin } = req.body;
    try {
        const user = await User.create({ name, email, password, isAdmin });
        res.status(200).json(user);
    } catch (error) {
        res.status(400).json({ message: error.message });
    }
}