const JwtStrategy = require('passport-jwt').Strategy;
const ExtractJwt = require('passport-jwt').ExtractJwt;
const db = require("../models");
const user = db.user;

const opts = {};

opts.jwtFromRequest = ExtractJwt.fromAuthHeaderAsBearerToken();
opts.secretOrKey = "secret";

module.exports = passport => {
  passport.use(
    new JwtStrategy(opts, (jwt_payload, done) => {

      user.findByPk(jwt_payload.id, { raw: true }).then(async result => {
        if (result) {
          let user = {
            id: result.id,
            username: result.username,
            name: result.name,
            age: result.age,
            gender: result.gender,
          }




          return done(null, user);
        } else return done(null, false);
      }).catch(err => console.log(err));
    }));
};
